import html
import os

import fooster.web.json
import fooster.web.page


class Scoreboard(fooster.web.page.PageHandler):
    directory = os.path.dirname(os.path.abspath(__file__)) + '/html'
    page = 'index.html'

    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', None)
        self.directory = self.template if self.template else self.directory

        self.sync = kwargs.pop('sync', None)

        super().__init__(*args, **kwargs)

    def format(self, page):
        with self.sync.lock:
            table = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(html.escape(service)) for service in self.sync.services)
            if self.sync.show.value:
                table += '<th>Score</th>'
            table += '\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'

            for name in self.sync.teams:
                scores = {score['service']: score['status'] for score in self.sync.scores[name] if score['service'] in self.sync.services}
                table += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(html.escape(name)) + ''.join('<td class="{}">{}</td>'.format('up' if scores[service] else 'down', 'Up' if scores[service] else 'Down') for service in self.sync.services)
                if self.sync.show.value:
                    table += '<td>{}</td>'.format(sum(score['score'] for score in self.sync.scores[name]))
                table += '\n\t\t</tr>'

            table += '\n\t</tbody>\n</table>'

            return page.format(refresh=self.sync.interval.value, scoreboard=table)


class ScoreboardJSON(fooster.web.json.JSONHandler):
    def __init__(self, *args, **kwargs):
        self.sync = kwargs.pop('sync', None)

        super().__init__(*args, **kwargs)

    def do_get(self):
        with self.sync.lock:
            status = {
                'services': list(self.sync.services),
                'teams': list(self.sync.teams),
                'scores': {},
            }

            for name in self.sync.teams:
                status['scores'][name] = {
                    'services': {score['service']: score['status'] for score in self.sync.scores[name] if score['service'] in self.sync.services},
                }

                if self.sync.show.value:
                    status['scores'][name]['score'] = sum(score['score'] for score in self.sync.scores[name])

            return 200, status
