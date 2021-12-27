
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Book, Author, BookInstance, Genre
import datetime
from catalog.forms import RenewBookForm



def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class LibrariansBookListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan to any user."""
    model = BookInstance
    paginate_by = 30
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/librarians_bookinstance_list_borrowed.html'

    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author 
    paginate_by = 10

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author 



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# Using generic views for simpler form handling:
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author

# TODO: add permissions to these three defs, using PermissionRequiredMixin
class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    #permission_required = 'catalog.can_mark_returned'
    # TODO: write tests for this class.  Remember that you need to check anything 
    # that you specify or that is part of the design. This will include who has 
    # access, the initial date, the template used, and where the view redirects on success.


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


# TODO: add permissions to these three defs, using PermissionRequiredMixin
class BookCreate(CreateView):
    model = Book 
    fields = ['title', 'author', 'summary', 'isbn']

class BookUpdate(UpdateView):
    model = Book 
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book 
    success_url = reverse_lazy('books')

