from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.html import escape
from lists.models import Item, List
from lists.forms import ItemForm


def homePage(request):
    return render(request, 'lists/home.html', {'form':ItemForm()})

'''
def viewList(request, listID):
    list_ = List.objects.get(id=listID)
    form = ItemForm()
    if request.method=='POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            Item.objects.create(text=request.POST['text'], list=list_)
            return redirect(reverse('lists:viewList', args=(list_.id, )))
    return render(request, 'lists/list.html', {'list':list_, 'form':form})
'''

def viewList(request, listID):
    list_ = List.objects.get(id=listID)
    form = ItemForm()
    if request.method=='POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            form.save(forList=list_)
            return redirect(reverse('lists:viewList', args=(list_.id, )))
    return render(request, 'lists/list.html', {'list':list_, 'form':form})


def newList(request):
    list_ = List.objects.create()
    item = Item(text=request.POST.get('itemText'), list=list_)
    try:
        item.full_clean()
        item.save()
    except ValidationError:
        list_.delete()
        error = escape('清單項目不能空白')
        return render(request, 'lists/home.html', {'error':error})
    return redirect(reverse('lists:viewList', args=(list_.id, )))