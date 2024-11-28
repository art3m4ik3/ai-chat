# POST /chat

Необходимо ставить Cookie "session" для прохождения авторизации. Подробнее об авторизации ниже.

Payload:

```json
{ "messages": [{ "role": "user", "content": "Hello!" }] }
```

Где "role" - ставить "system", "assistant" или "user"
Где "content" - текст сообщения
Также можно делать несколько сообщений по такому же типу

Ответ:

```json
{ "response": "Hello!" }
```

Где "response" - текст ответа<br>
Примечание: обычно только латинские буквы, символы и цифры могут отображаются как надо, в остальных случаях как Unicode

# POST /register

Payload:

```json
{ "username": "cat", "password": "123qwe", "confirm_password": "123qwe" }
```

Где "username" - имя пользователя
Где "password" - пароль
Где "confirm_password" - подтверждение пароля

При успешном ответе вернет статус 302, сделает редирект на главную, установит Cookie "session"

# POST /login

Payload:

```json
{ "username": "cat", "password": "123qwe" }
```

Где "username" - имя пользователя
Где "password" - пароль

При успешном ответе вернет статус 302, сделает редирект на главную, установит Cookie "session"
