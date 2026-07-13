from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from budget.models import Transaction


class SummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()
        month_start = today.replace(day=1)

        monthly_transactions = Transaction.objects.filter(date__gte=month_start)
        total_this_month = monthly_transactions.aggregate(total=Sum('amount'))['total'] or 0

        context['total_this_month'] = total_this_month
        context['recent_transactions'] = Transaction.objects.all()[:5]
        context['month_label'] = today.strftime('%Y年%m月')

        return context


class BudgetListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/budget_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = self.request.GET.get('category', '')
        transactions = Transaction.objects.all()

        if category:
            transactions = transactions.filter(category=category)

        context['transactions'] = transactions
        context['categories'] = (
            Transaction.objects.values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        context['selected_category'] = category
        context['total'] = transactions.aggregate(total=Sum('amount'))['total'] or 0

        return context