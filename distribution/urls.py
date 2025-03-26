from django.urls import path
from distribution.apps import DistributionConfig
from distribution.views import ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, MessageListView, \
    MessageCreateView, MessageUpdateView, MessageDeleteView, MailingSettingsListView, MailingSettingsCreateView, \
    MailingSettingsUpdateView, MailingSettingsDeleteView, MailingSettingsDetailView, LogListView, MessageDetailView, \
    ClientDetailView

app_name = DistributionConfig.name

urlpatterns = [
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('client/create', ClientCreateView.as_view(), name='create_client'),
    path('client/edit/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),
    path('client/delete/<int:pk>/', ClientDeleteView.as_view(), name='delete_client'),
    path('message', MessageListView.as_view(), name='message_list'),
    path('message/create', MessageCreateView.as_view(), name='create_message'),
    path('message/edit/<int:pk>/', MessageUpdateView.as_view(), name='update_message'),
    path('message/delete/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),
    path('', MailingSettingsListView.as_view(), name='distribution_list'),
    path('distribution/<int:pk>/', MailingSettingsDetailView.as_view(), name='distribution_detail'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('distribution/create', MailingSettingsCreateView.as_view(), name='create_distribution'),
    path('distribution/edit/<int:pk>/', MailingSettingsUpdateView.as_view(), name='update_distribution'),
    path('distribution/delete/<int:pk>/', MailingSettingsDeleteView.as_view(), name='delete_distribution'),
    path('log', LogListView.as_view(), name='log_list')
]
