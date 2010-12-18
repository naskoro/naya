**naya.app**
 | - добавить app.log();
 | ? прорефакторить url_for, часто используемая функция, нужно больше удобства;
 | - сделать что-то подобное werkzeug.Href, но с любым урлом Href('/test?test=42') и т.п.;

**naya.conf**
 | ? прорефактоорить обработку ошибок, сделать свои Errors;

**naya.jinja**
 | + прорефакторить значения в path_allow, path_deny;

**naya.marker**
 | ? возможность поставить after, before;
 | - возможность задать ручную сортировку для маркеров через конфиг;
 | - сделать маркер для middleware;

**naya.script**
 | - написать что-то типа call_command;
 | - переделать тестирование для make_shell, чтоб учитывался coverage-м;
 | - перехват stdin;

**naya.testing**
 | + заменить __getattribute__ на __getattr__;
