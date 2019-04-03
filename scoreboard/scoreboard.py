import os

import fooster.web.json
import fooster.web.page

import scoreboard.sync


def gen(config, template):
    class Scoreboard(fooster.web.page.PageHandler):
        directory = template if template else os.path.dirname(os.path.abspath(__file__)) + '/html'
        page = 'index.html'
        interval = config.interval

        def format(self, page):
            with scoreboard.sync.lock:
                html = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(service) for service in scoreboard.sync.services)
                if config.show:
                    html += '<th>Score</th>'
                html += '\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'

                for name in scoreboard.sync.teams:
                    html += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td class="{}">{}</td>'.format('up' if score['status'] else 'down', 'Up' if score['status'] else 'Down') for score in scoreboard.sync.scores[name] if score['service'] in scoreboard.sync.services)
                    if config.show:
                        html += '<td>{}</td>'.format(sum(score['score'] for score in scoreboard.sync.scores[name]))
                    html += '\n\t\t</tr>'

                html += '\n\t</tbody>\n</table>'

                return page.format(refresh=Scoreboard.interval, scoreboard=html)

    return Scoreboard


def gen_json(config):
    class ScoreboardJSON(fooster.web.json.JSONHandler):
        def do_get(self):
            with scoreboard.sync.lock:
                status = {
                    'services': list(scoreboard.sync.services),
                    'teams': list(scoreboard.sync.teams),
                    'scores': {},
                }

                for name in scoreboard.sync.teams:
                    status['scores'][name] = {
                        'services': {score['service']: score['status'] for score in scoreboard.sync.scores[name] if score['service'] in scoreboard.sync.services},
                    }

                    if config.show:
                        status['scores'][name]['score'] = sum(score['score'] for score in scoreboard.sync.scores[name])

                return 200, status

    return ScoreboardJSON
