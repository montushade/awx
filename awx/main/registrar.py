from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from signals import activity_stream_create, activity_stream_update, activity_stream_delete

class ActivityStreamRegistrar(object):

    def __init__(self):
        self.models = []

    def connect(self, model):
        #(receiver, sender=model, dispatch_uid=self._dispatch_uid(signal, model))
        if model not in self.models:
            self.models.append(model)
            post_save.connect(activity_stream_create, sender=model, dispatch_uid=self.__class__ + str(model) + "_create")
            pre_save.connect(activity_stream_update, sender=model, dispatch_uid=self.__class__ + str(model) + "_update")
            post_delete.connect(activity_stream_delete, sender=model, dispatch_uid=self.__class__ + str(model) + "_delete")

            for m2mfield in model._meta.many_to_many:
                m2m_attr = get_attr(model, m2mfield.name)
                m2m_changed.connect(activity_stream_associate, sender=m2m_attr.through,
                                    dispatch_uid=self.__class__ + str(m2m_attr.through) + "_associate")

    def disconnect(self, model):
        if model in self.models:
            post_save.disconnect(dispatch_uid=self.__class__ + str(model) + "_create")
            pre_save.disconnect(dispatch_uid=self.__class__ + str(model) + "_update")
            post_delete.disconnect(dispatch_uid=self.__class__ + str(model) + "_delete")
            self.models.pop(model)


            for m2mfield in model._meta.many_to_many:
                m2m_attr = get_attr(model, m2mfield.name)
                m2m_changed.disconnect(dispatch_uid=self.__class__ + str(m2m_attr.through) + "_associate")

activity_stream_registrar = ActivityStreamRegistrar()
