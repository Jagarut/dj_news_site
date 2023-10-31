from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse

from .models import Article
from .forms import CommentForm

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"

class CommentGet(DetailView):
    model = Article
    template_name = "article_detail.html"

    # adds a CommentForm instance to the context, making the form available for rendering in the associated template
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context

class CommentPost(SingleObjectMixin, FormView): # new
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # from SingleObjectMixin that lets us grab the article pk from the URL
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        # called when form validation has succeeded
        comment = form.save(commit=False)
        comment.article = self.object
        comment.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        article = self.get_object()
        return reverse("article_detail", kwargs={"pk": article.pk})

class ArticleDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = (
        "title",
        "body",
    )
    template_name = "article_edit.html"

    def test_func(self): 
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self): 
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleCreateView(LoginRequiredMixin, CreateView): 
    model = Article
    template_name = "article_new.html"
    fields = (
        "title",
        "body",
    )
    # customize the behavior of a view when a form is valid. 
    # In the provided code, it assigns the currently logged-in user as the author of the form data 
    # and then proceeds to save the form data using the parent class's form_valid method
    def form_valid(self, form): 
        form.instance.author = self.request.user
        return super().form_valid(form)