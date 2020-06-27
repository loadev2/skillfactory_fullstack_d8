from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category


def index(request):

    # 1st version
    # counts = {t.name: random.randint(1, 100) for t in Tag.objects.all()}

    # 2nd version
    # counts = {t.name: t.taggit_taggeditem_items.count()
    # for t in Tag.objects.all()}

    # 3rd version
    from django.db.models import Count

    #counts = Category.objects.annotate(total_tasks=Count('todoitem')).order_by("-total_tasks")
    counts = Category.objects.all()
    counts = {c.name: c.todos_count for c in counts}

    if not TodoItem.isInit:
        TodoItem.priorities_count[TodoItem.PRIORITY_LOW]=TodoItem.objects.filter(priority = TodoItem.PRIORITY_LOW).count()
        TodoItem.priorities_count[TodoItem.PRIORITY_MEDIUM] = TodoItem.objects.filter(priority=TodoItem.PRIORITY_MEDIUM).count()
        TodoItem.priorities_count[TodoItem.PRIORITY_HIGH] = TodoItem.objects.filter(
            priority=TodoItem.PRIORITY_HIGH).count()
        TodoItem.isInit = True

    priorities_count = {
        TodoItem.PRIORITY_CHOICES[0][1]: TodoItem.priorities_count[TodoItem.PRIORITY_HIGH],
        TodoItem.PRIORITY_CHOICES[1][1]: TodoItem.priorities_count[TodoItem.PRIORITY_MEDIUM],
        TodoItem.PRIORITY_CHOICES[2][1]: TodoItem.priorities_count[TodoItem.PRIORITY_LOW]
    }
    return render(request, "tasks/index.html", {"counts": counts, "priorities": priorities_count})


def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        for t in user_tasks:
            tags.append(list(t.category.all()))

        categories = []
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)
        context["categories"] = categories

        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"
