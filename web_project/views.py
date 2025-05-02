from django.views.generic import TemplateView as BaseTemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

class TemplateView(LoginRequiredMixin, BaseTemplateView):
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        return TemplateLayout.init(self, super().get_context_data(**kwargs))

class SystemView(TemplateView):
    template_name = "pages/system/not-found.html"
    status = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_status'] = getattr(self, 'status', 400)
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("system.html", context),
                "status": self.status,
            }
        )
        return context
