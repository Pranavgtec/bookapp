from django.urls import path
from ecommerceapp import views

urlpatterns = [
  path('signup/',views.RegistrationView.as_view(),name='signup'),
  path('',views.IndexView.as_view(),name='home'),
  path('profile-edit/<int:pk>/',views.EditProfileView.as_view(),name='profile-edit'),
  path('login/',views.LoginView.as_view(),name='login'),
  path('logout',views.LogoutView.as_view(),name='logout'),
  path('book-create/',views.CreateBookView.as_view(),name='book-create'),
  path('tag-create/',views.CreateTagView.as_view(),name='tag-create'),
  path('author-create/',views.CreateAuthorView.as_view(),name='author-create'),
  path('book-detail/<int:pk>/',views.BookDetailView.as_view(),name='book-detail'),
  path('add_to_cart/<int:pk>/',views.AddCartView.as_view(),name='addtocart'),
  path('cart/',views.CartView.as_view(),name='cart'),
  path('about/',views.AboutView.as_view(),name='about'),
  path('delivery-detail/',views.DeliveryView.as_view(),name='delivery-detail'),
  path('cartitem-delete/<int:pk>/',views.CartItemDeleteView.as_view(),name='cartitem-delete'),
  path('checkout/',views.CheckoutView.as_view(),name='checkout'),
  path('pay-verify/',views.PaymentVerificationView.as_view(),name='pay-verify'),
  path('book-search/',views.BooksSearchView.as_view(),name='book-search'),
  path('paid-books/',views.BookPaymentHistoryView.as_view(),name='paid-books'),
  path('review/<int:pk>/',views.BookReviewView.as_view(),name='review'),
  path('dashboard/',views.DashboardView.as_view(),name='dashboard'),
  path('book-update/<int:pk>/',views.BookUpdateView.as_view(),name='book-update'),
  path('book-delete/<int:pk>/',views.BookDeleteView.as_view(),name='book-delete'),
  path('no_permission/',views.NOPermissionView.as_view(),name='no_permission'),
  path('book-list/',views.BookListView.as_view(),name='book_list'),
  path('favourites/',views.BookFavouritesView.as_view(),name='favourite_books'),
  path('delete-favourite/<int:pk>/',views.BookFavouriteDeleteView.as_view(),name='delete_favourite'),
  path('profile/',views.BookProfileView.as_view(),name='profile'),
  path('cash_on_delivery/',views.CashOnDeliveryView.as_view(),name='cash_on_delivery'),
  path('contactus/',views.ContactUsView.as_view(),name='contactus'),
  path('livechat/',views.LiveChatView.as_view(),name='livechat'),
  path('admin/livechat/<int:inquiry_id>/', views.AdminChatDetailView.as_view(), name='admin_chat_detail'),

  
]
