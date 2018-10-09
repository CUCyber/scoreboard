import os

import fooster.web.page

import scoreboard.sync


def gen(config, template):
    class Scoreboard(fooster.web.page.PageHandler):
        directory = template if template else os.path.dirname(os.path.abspath(__file__)) + '/html'
        page = 'index.html'
        interval = config.interval

        def format(self, page):
            with scoreboard.sync.lock:
                html = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(service) for service in scoreboard.sync.services) + '<th>Score</th>\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'

                for name, items in scoreboard.sync.scores.items():
                    html += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td class="{}">{}</td>'.format('up' if score['status'] else 'down', 'Up' if score['status'] else 'Down') for score in items if score['service'] in scoreboard.sync.services) + '<td>{}</td>\n\t\t</tr>'.format(sum(score['score'] for score in items))

                html += '\n\t</tbody>\n</table>'

                return page.format(refresh=Scoreboard.interval, scoreboard=html)

    return Scoreboard
