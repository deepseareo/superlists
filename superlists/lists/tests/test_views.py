from django.test import TestCase
from django.core.urlresolvers import resolve, reverse
from lists.views import homePage
from lists.models import Item, List
from lists.forms import ItemForm
from lists.forms import EMPTY_ITEM_ERROR

 

class HomePageTest(TestCase):


    def test_root_url_resolves_to_homePage_view(self):
        found = resolve('/')
        self.assertEqual(found.func, homePage)


    def test_homePage_returns_correct_HTML(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')


    def test_homePage_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')        


    def test_homePage_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)



class ListViewTest(TestCase):

    def test_use_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(reverse('lists:viewList', args=(list_.id, )))
        self.assertTemplateUsed(response, 'lists/list.html')


    def test_displays_only_items_for_that_list(self):
        correctList = List.objects.create() 
        Item.objects.create(text='itemey 1', list=correctList)
        Item.objects.create(text='itemey 2', list=correctList)
        
        response = self.client.get(reverse('lists:viewList', args=(correctList.id, ))) 

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2') 
        

    def test_can_save_a_POST_request_to_an_existing_list(self):
        correctList = List.objects.create()
        self.client.post(
            reverse('lists:viewList', args=(correctList.id, )),
            data={'text':'目前清單的新項目'}
        )
        self.assertEqual(Item.objects.count(), 1)
        id_text = Item.objects.first()
        self.assertEqual(id_text.text, '目前清單的新項目')
        self.assertEqual(id_text.list, correctList)


    def test_POST_redirect_to_list_view(self):
        correctList = List.objects.create()
        response = self.client.post(
            reverse('lists:viewList', args=(correctList.id, )),
            data={'text':'目前清單的新項目'}
        )
        self.assertRedirects(response, reverse('lists:viewList', args=(correctList.id, )))
    
    
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(reverse('lists:viewList', args=(list_.id, )), data={'text':''})


    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)
    
    
    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')


    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ItemForm)


    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, EMPTY_ITEM_ERROR)
    

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(reverse('lists:viewList', args=(list_.id, )))
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertContains(response, 'name="text"')



class NewListTest(TestCase):


    def test_saving_a_POST_request(self):
        self.client.post(reverse('lists:newList'), data={'text':'新的項目'})
        self.assertEqual(Item.objects.count(), 1)
        id_text = Item.objects.first()
        self.assertEqual(id_text.text, '新的項目')


    def test_redirect_after_POST(self):
        response = self.client.post(reverse('lists:newList'), data={'text':'新的項目'})
        newList = List.objects.first()
        self.assertRedirects(response, reverse('lists:viewList', args=(newList.id, )))


    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post(reverse('lists:newList'), data={'text':''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')


    def test_validation_error_are_shown_on_home_page(self):
        response = self.client.post(reverse('lists:newList'), data={'text':''})
        self.assertContains(response, EMPTY_ITEM_ERROR)


    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post(reverse('lists:newList'), data={'text':''})
        self.assertIsInstance(response.context['form'], ItemForm)


    def test_invalid_list_item_arent_saved(self):
        self.client.post(reverse('lists:newList'), data={'text':''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
