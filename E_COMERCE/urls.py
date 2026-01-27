from django.urls import path
from E_COMERCE import views,services

urlpatterns = [
    #auth
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin/dashboard/sales-data/', views.sales_chart_data, name='sales_chart_data'),
    path('admin/analytics/visiting-users-data/', views.visiting_users_data, name='visiting_users_data'),


    path('login/', views.LoginView.as_view(), name='log_in'), 
    path('signin/', views.SigninView.as_view(), name='sign_up'), 
    path('logout/', views.LogoutView.as_view(), name='log_out'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password'),

    #user
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
    path('admin/users/toggle-status/<int:user_id>/', views.ToggleUserStatusView.as_view(), name='toggle_user_status'),
    path('admin/users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('admin/users/update/<int:user_id>/', views.UserUpdateView.as_view(), name='user_update'),

    #product
    path('', views.HomeView.as_view(), name='home'), 
    path('admin/product/',views.ProductListView.as_view(),name='product'),
    path('admin/product/create/',views.ProductCreateView.as_view(),name='product_create'),
    path('admin/product/update/<int:product_id>/',views.ProductUpdateView.as_view(),name='Product_update'),
    path('product/details/<int:item_id>/',views.ProductDetailsView.as_view(),name = 'product_details'),
    path('review/create/',views.RatingCreateView.as_view(),name = 'rating_create'),
    path('product/toggle-status/<int:product_id>/', views.ProductToggleStatusView.as_view(), name='product_toggle'),
    path('category/products/search/', services.category_product_search, name='category_product_search'),
    
    #category
    path('admin/',views.AdminHomeView.as_view(),name='admin'),
    path('admin/category/',views.CategoryListView.as_view(),name='category'),
    path('admin/category/create/',views.CategoryCreateView.as_view(),name='category_create'),
    path('admin/category/update/<int:category_id>/',views.CategoryUpdateView.as_view(),name='category_update'),
    path('admin/category/toggle-status/<int:category_id>/',views.ToggleCategoryStatusView.as_view(), name='toggle_category_status'),
    
    #subcategory
    path('admin/subcategory/',views.SubCategoryListView.as_view(),name='subcategory'),
    path('admin/subcategory/create/',views.SubCategoryCreateView.as_view(),name='subcategory_create'),
    path('admin/subcategory/update/<int:subcategory_id>/',views.SubCategoryUpdateView.as_view(),name='subcategory_update'),
    path('admin/subcategory/toggle-status/<int:subcategory_id>/',views.ToggleSubCategoryStatusView.as_view(), name='subcategory_toggle_status'),
    
    #productitem
    path('admin/productitem/',views.ProductItemListView.as_view(), name='productitem_list'),
    path('admin/productitem/create/',views.ProductItemCreateView.as_view(), name='productitem_create'),
    path('admin/productitem/<int:productitem_id>/update/',views.ProductItemUpdateView.as_view(), name='productitem_update'),
    path('admin/productitem/toggle-status/<int:productitem_id>/',views.ProductItemToggleStatusView.as_view(), name='productitem_toggle_status'),



    #admin poster
    path('admin/poster/',views.PosterListView.as_view(), name='admin_poster_list'),
    path('admin/poster/create/',views.AdminPosterCreateView.as_view(), name='admin_poster_create'),
    path('admin/poster/update/<int:poster_id>/',views.AdminPosterUpdateView.as_view(), name='admin_poster_update'),
    path('admin/poster/toggle-status/<int:poster_id>/',views.AdminPosterToggleStatusView.as_view(), name='admin_poster_toggle_status'),

    #wishlist
    path('wishlist/',views.WishlistDetailsView.as_view(),name='user_wishlist'),
    path('wishlist/delete/',views.WishlistDeleteView.as_view(),name='wishlist_delete'),
    path('wishlist/create_update/',views.WishlistCreateUpdateView.as_view(),name='wishlist_create_update'),

    #cart
    path('cart/',views.CartDetailsView.as_view(),name='user_cart'),
    path('cart/create/',views.CartCreateView.as_view(),name='cart_create'),
    path('cart/update/<int:cart_id>/',views.CartUpdateView.as_view(),name='cart_update'),
    path('cart/delete/<int:cart_id>/',views.CartDeleteView.as_view(),name='cart_delete'),
    path('category/products/<int:category_id>/',views.CategoryProductsListView.as_view(),name='category_product_list'),
    path('api/all/category/',views.CategoryApiListView.as_view(),name='api_category_list'),
    
    #admin cart
    path('admin/cart/',views.AdminCartListView.as_view(), name='admin_cart_list'),
    path('admin/cart/toggle-status/<int:cart_id>/',views.AdminCartToggleStatusView.as_view(), name='toggle_cart_status'),
    path('admin/cart/create/', views.AdminCartCreateView.as_view(), name='admin_cart_create'),
    path('admin/cart/update/<int:pk>/',views.AdminCartUpdateView.as_view(), name='admin_cart_update'),


    #admin cartitem
    path('admin/cartitem/',views.AdminCartItemListView.as_view(), name='admin_cartitem_list'),
    path('admin/cartitem/create/',views.AdminCartItemCreateView.as_view(), name='admin_cartitem_create'),
    path('admin/cartitem/update/<int:pk>/',views.AdminCartItemUpdateView.as_view(), name='admin_cartitem_update'),
     path('admin/cartitem/toggle-status/<int:cartitem_id>/', views.AdminCartItemToggleStatusView.as_view(), name='admin_cartitem_toggle_status'),

    #admin wishlist
    path('admin/wishlist/',views.AdminWishlistListView.as_view(), name='admin_wishlist_list'),
    path('admin/wishlist/toggle-status/<int:pk>/',views.AdminWishlistToggleStatusView.as_view(), name='toggle_wishlist_status'),
    path('admin/wishlist/create/',views.AdminWishlistCreateView.as_view(), name='admin_wishlist_create'),
    path('admin/wishlist/update/<int:pk>/',views.AdminWishlistUpdateView.as_view(), name='admin_wishlist_update'),
    path('admin/api/product-items/<int:product_id>/',views.AdminProductItemByProductView.as_view(), name='api_product_items_by_product'),

    #order
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('order/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('direct-order/create/<int:item_id>/', views.DirectOrderView.as_view(), name='direct_order'),
    path('cart/update/<int:pk>/', views.CartItemUpdateView.as_view(), name='cart_item_update'),
    path('cart/remove/<int:pk>/', views.CartItemRemoveView.as_view(), name='cart_item_remove'),


    #admin order

    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/orders/create/', views.AdminOrderCreateView.as_view(), name='admin_order_create'),
    path('admin/orders/update/<int:pk>/', views.AdminOrderUpdateView.as_view(), name='admin_order_update'),
    path('admin/orders/toggle-status/<int:pk>/', views.AdminOrderToggleStatusView.as_view(), name='admin_order_toggle_status'),

    
    #admin offer
    path('admin/offers/',views.OfferListView.as_view(), name='offer_list'),
    path('admin/offers/create/',views.OfferCreateView.as_view(), name='offer_create'),
    path('admin/offers/<int:pk>/update/',views.OfferUpdateView.as_view(), name='offer_update'),
    path('admin/offer/toggle-status/<int:pk>/',views.OfferToggleStatusView.as_view(), name='offer_toggle_status'),

    #admin orderitem
    path('admin/orderitems/', views.AdminOrderItemListView.as_view(), name='admin_orderitem_list'),
    path('admin/orderitems/create/', views.AdminOrderItemCreateView.as_view(), name='admin_orderitem_create'),
    path('admin/orderitems/update/<int:pk>/', views.AdminOrderItemUpdateView.as_view(), name='admin_orderitem_update'),
    path('admin/orderitems/toggle-status/<int:pk>/', views.AdminOrderItemToggleStatusView.as_view(), name='admin_orderitem_toggle_status'),

    path('track_order/<int:order_id>/',views.TrackOrderView.as_view(), name='track_order'),
    path('payment/create/<int:order_id>/',views.PaymentCreateView.as_view(), name='payment_create'),
    path('order/delete/<int:order_id>/', views.OrderDeleteView.as_view(), name='order-delete'),
]
