# business_mail

Сервис для учёта и отслеживания почтовых отправлений небольшой компании «Деловая почта города», оказывающей курьерские, почтовые услуги.
Обеспечивает взаимодействие с АИС «Налог-3» Федеральной налоговой службы.
Сервис успешно функционирует (https://dpochta.ru, функционал доступен только для сотрудников компании и ФНС).

Краткий фукционал:
- Добавление реестров почтовых отправлений сотрудником ФНС.
- Генерация трек-номера для каждого почтового отправления.
- Хранение информации о каждом отправлении (текущий статус и история, ФИО получателя, адрес, отправитель, ФИО инспектора... ) в БД.
- Поиск и отслеживание отправления по трек-номеру.
- Ведение статистики почтовых отправлений.
- Печать извещений для получателей работником почтовой службы.
- Загрузка реестра отправлений в БД, печать реестра, хранение информации о реестрах в БД.
- Загрузка перечня отсканированных отправлений с присвоением соответствующего статуса.
- Информирование о критических действиях пользователей в Telegram-группу администратора.
- Периодическое резервное копирование БД.

Сервис построен на Django, для его запуска используется Docker-compose.
nginx, docker, python c uvcorn запускаются каждый в своем контейнере для удобства запуска.


Post accounting and tracking service for small company "Business Post of the City", which provides courier and postal services.
Provides interaction with the AIS "Nalog-3" of the Federal Tax Service.
The service is successfully functioning (https://dpochta.ru, the functionality is available only for employees of the company and the Federal Tax Service).

Functionality:
- Adding registers of postal items by an employee of the Federal Tax Service.
- Generation of track numbers for each postal item.
- Storage of information about each shipment (current status and history, full name of the recipient, address, sender, full name of the inspector ...) in the database.
- Search and tracking the shipment by track number.
- Maintaining postage statistics.
- Printing notices for recipients by a postal worker.
- Loading the register of shipments into the database, printing the register, storing information about the registers in the database.
- Downloading a list of scanned items with the assignment of the appropriate status.
- Informing about critical user actions in the administrator's Telegram group.
- Periodic database backup.

The service is built on Django and uses Docker-compose to run it.
nginx, docker, python with uvcorn run each in their own container for easy launch.