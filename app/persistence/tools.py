from . import *

LOG = logging.getLogger('LaVidaModerna_Bot.persistence.tools')


@db_session
def get_latest_used_sounds_from_user(user_id, limit=3):
    user = User.get(id=user_id)
    if user:
        results = Sound.select_by_sql('SELECT Sound.* '
                                      'FROM Sound, ResultHistory '
                                      'WHERE Sound.disabled = 0 AND '
                                      'ResultHistory.sound = Sound.id '
                                      'AND ResultHistory.user = $user '
                                      'GROUP BY Sound.id '
                                      'ORDER BY ResultHistory.timestamp DESC;', globals={'user': user.id})[:limit]
        LOG.debug("Obtained %d latest used sound results.", len(results))
        return [object_to_sound(sound) for sound in results]
    else:
        return []
