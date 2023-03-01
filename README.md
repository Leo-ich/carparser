### Cборка docker image:

    docker build -t carparser ./

### Запуск контейнера в podman или docker:
Создаём volume для хранения базы данных вне докера:

    docker volume create v_datadir
Запускаем:

    docker run -it --rm -v v_datadir:/home/appuser/datadir carparser:latest

Это запишет данные парсера в папку volumes на хост машине,
 /home/"username"/.local/share/containers/storage/volumes/v_datadir для podman.
Подобным образом можно сохранять данные в Amazon S3 или EBS.

Для сохранения данных в вами указанную папку запускаем:
    
    docker run -it --rm --userns=keep-id -v $(realpath ~/datadir):/home/appuser/datadir:z carparser:latest

Это запишет данные парсера в файл базы данных в папке /home/"username"/datadir 
на хост машине. При таком запуске работающий firefox на хосте приводит к падению 
firefox в докере. Также не применяйте z или Z к системным папкам (/home) это 
приведёт к тому что ваша хост машина может перестать загружаться (баги docker).