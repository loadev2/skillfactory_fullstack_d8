from django.db.models.signals import m2m_changed, post_save, post_delete, post_init, class_prepared
from django.dispatch import receiver
from tasks.models import TodoItem, Category
from collections import Counter


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    for cat in instance.category.all():
        slug = cat.slug

        new_count = 0
        for task in TodoItem.objects.all():
            new_count += task.category.filter(slug=slug).count()
        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, pk_set, **kwargs):
    if not action in ["post_remove"]:
        return
    for cat in Category.objects.filter(pk__in=pk_set):
        new_count = cat.todos_count - 1
        Category.objects.filter(slug=cat.slug).update(todos_count=new_count)


@receiver(post_save, sender=TodoItem)
def task_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if not created:
        count_tasks = TodoItem.objects.filter(priority=instance.priority).count()
        TodoItem.priorities_count[instance.priority] = count_tasks
        return
    TodoItem.priorities_count[instance.priority] += 1


@receiver(post_delete, sender=TodoItem)
def task_delete(sender, instance, using, **kwargs):
    TodoItem.priorities_count[instance.priority] -= 1


