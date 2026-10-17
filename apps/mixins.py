from django.contrib import messages


class ConfirmDeleteMixin:
    """
    mixin مشترک برای همه DeleteViewها؛ همه از یک تمپلیت استفاده می‌کنند:
    templates/pos/confirm_delete.html
    """

    template_name = "pos/confirm_delete.html"

    entity_name = ""                      # مثلاً «دسته‌بندی»
    cancel_url = None                     # اگر خالی باشد، success_url
    warning_text = "در صورت حذف، این عملیات قابل بازگشت نیست."
    success_message = ""

    def get_object_label(self):
        return str(self.object)

    def get_details(self):
        return None

    def get_warning_text(self):
        return self.warning_text

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "entity_name": self.entity_name,
            "object_label": self.get_object_label(),
            "cancel_url": str(self.cancel_url or self.success_url),
            "warning_text": self.get_warning_text(),
            "details": self.get_details(),
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response