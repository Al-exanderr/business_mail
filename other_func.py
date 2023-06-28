import os


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def download_file(request):
    _file = 'shpi_list.xlsx'
    filename = os.path.basename(_file)
    response = FileResponse(FileWrapper(open(filename, 'rb')), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment; filename=%s" % _file
    return response


def handle_uploaded_file(f1, f2):
    '''Обработчик загружаемого файла. f1 - исх файл, f2 - файл назначения'''
    with open(f2, 'wb+') as destination:
        for chunk in f1.chunks():
            destination.write(chunk)
