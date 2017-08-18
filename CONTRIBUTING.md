# How to contribute

We are not stringent with that. Just do a fork, do some contributions and
send us a Pull Request. Do not forget to write tests and to describe well
what your contributions are. It will help us at review process :)

## Setting up environment

We use [docker](https://www.docker.com/) for local development.
To run the entire Network API and its dependencies just run:

```bash
$> docker-compose up -d
```

## Writing tests

We use [Nose](http://nose.readthedocs.io/en/latest/) with
[Django](https://www.djangoproject.com/) for tests.
You can find tests files and check our tests code style.
To run tests do the following:

```bash
$> docker exec -it netapi_app ./fast_start_test.sh
```

If you need to run specific tests you can it by running:

```bash
docker exec -it netapi_app ./fast_start_test.sh networkapi/plugins/SDN/
```
