import os
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required


# @permission_required('utilities.view_generic')
def protected_media(request, filename):
    print(filename,'filename')
    """
    View to send file via X-Sendfile
    :param request: the HTTP request
    :param filename: the filename, extracted from the url
    :return: a HttpResponse object
    """
    # Construct full path and base name
    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    base_name = os.path.basename(filename)

    # Check whether the file exist
    if not os.path.exists(full_path):
        raise Http404(_("The requested file does not exist"))

    #Let Django serve it if the XSENDFILE setting is false
    if not settings.XSENDFILE:
        from django.views.static import serve
        return serve(request, full_path, document_root='/')

    # Determine the mime type
    (mime_type, encoding) = mimetypes.guess_type(full_path)

    # Construct the response
    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'inline;filename='+base_name
    response['X-Sendfile'] = full_path

    return response

@permission_required('utilities.view_generic')
def download_image(request, filename):
    print(filename,'filename')
    """
    View to send file via X-Sendfile
    :param request: the HTTP request
    :param filename: the filename, extracted from the url
    :return: a HttpResponse object
    """
    # Construct full path and base name
    if filename.startswith('/media/'):  
        filename = filename[len('/media/'):]
        print(filename,'ok')
    if filename.startswith('media/'):  
        filename = filename[len('media/'):]
        print(filename,'ok')
    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    base_name = os.path.basename(filename)
    print(full_path,'full_path')

    # Check whether the file exist
    if not os.path.exists(full_path):
        raise Http404(_("The requested file does not exist"))

    #Let Django serve it if the XSENDFILE setting is false
    if not settings.XSENDFILE:
        from django.views.static import serve
        return serve(request, full_path, document_root='/')

    # Determine the mime type
    (mime_type, encoding) = mimetypes.guess_type(full_path)

    # Construct the response
    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'attachment;filename='+base_name
    response['X-Sendfile'] = full_path

    return response

