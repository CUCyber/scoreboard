import os

import fooster.web.page

import snakeboi.sync


def gen(cfg):
    class Scoreboard(fooster.web.page.PageHandler):
        directory = os.path.dirname(os.path.abspath(__file__)) + '/html'
        page = 'index.html'
        config = cfg

        def format(self, page):
            scoreboard = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(service) for service in Scoreboard.config.services) + '<th>Score</th>\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'
            for name, items in snakeboi.sync.scores.items():
                scoreboard += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td class="{}">{}</td>'.format('up' if score['status'] else 'down', 'Up' if score['status'] else 'Down') for score in items) + '<td>{}</td>\n\t\t</tr>'.format(sum(score['score'] for score in items))

            scoreboard += '\n\t</tbody>\n</table>'

            return page.format(refresh=Scoreboard.config.interval, scoreboard=scoreboard)

    return Scoreboard
