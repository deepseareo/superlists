from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from django.utils.html import escape
from lists.views import homePage
from lists.models import Item, List
from lists.forms import ItemForm


# Create your tests here.
class HomePageTest(TestCase):
    def test_root_url_resolves_to_homePage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, homePage)

    def test_根網址解析到homePage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, homePage)

    def test_homePage_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')


    def test_homePage_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):


    def test_顯示該清單的所有項目(self):
        correctList = List.objects.create()
        Item.objects.create(text='itemey 1', list=correctList)
        Item.objects.create(text='itemey 2', list=correctList)
        otherList = List.objects.create()
        Item.objects.create(text='other list item 1', list=otherList)
        Item.objects.create(text='other list item 2', list=otherList)
        response = self.client.get(reverse('lists:viewList', args=(correctList.id, )))
        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')
        '''
        response = self.client.get(reverse('lists:viewList', args=(otherList.id, )))
        self.assertNotContains(response, 'itemey 1')
        self.assertNotContains(response, 'itemey 2')
        self.assertContains(response, 'other list item 1')
        self.assertContains(response, 'other list item 2')
        '''

    def test_使用清單範本(self):
        list_ = List.objects.create()
        response = self.client.get(reverse('lists:viewList', args=(list_.id, )))
        self.assertTemplateUsed(response, 'lists/list.html')


    def test_validation_errors_end_up_on_list_page(self):
        list_ = List.objects.create()
        response = self.client.post(
            reverse('lists:viewList', args=(list_.id, )),
            data={'itemText':''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')
        expectedError = escape('清單項目不能空白')
        self.assertContains(response, expectedError)
        
        
        

class NewListTest(TestCase):


    def test_儲存POST請求(self):
        self.client.post(reverse('lists:newList'), data={'itemText':'新的項目'})
        self.assertEqual(Item.objects.count(), 1)
        newItem = Item.objects.first()
        self.assertEqual(newItem.text, '新的項目')


    def test_在POST之後轉址(self):
        response = self.client.post(reverse('lists:newList'), data={'itemText':'新的項目'})
        newList = List.objects.first()
        self.assertRedirects(response, reverse('lists:viewList', args=(newList.id, )))
 

class NewItemTest(TestCase):
    
    
    def test_可以將POST請求儲存到目前已有的清單(self):
        correctList = List.objects.create()
        self.client.post(
            reverse('lists:addItem', args=(correctList.id, )),
            data={'itemText':'目前清單的新項目'}
        )
        self.assertEqual(Item.objects.count(), 1)
        newItem = Item.objects.first()
        self.assertEqual(newItem.text, '目前清單的新項目')
        self.assertEqual(newItem.list, correctList)
    
    
    def test_轉址到viewList_view(self):
        #otherList = List.objects.create()
        correctList = List.objects.create()
        response = self.client.post(
            reverse('lists:addItem', args=(correctList.id, )),
            data={'itemText':'目前清單的新項目'}
        )
        self.assertRedirects(response, reverse('lists:viewList', args=(correctList.id, )))
        
        
          