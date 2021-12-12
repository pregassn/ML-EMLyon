'''See 

v1 https://gist.github.com/tvst/ef477845ac86962fa4c92ec6a72bb5bd
v2 https://gist.github.com/DavidS3141/822310a2ed9f600362ac31ee49223f86
'''
try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
    from streamlit.ScriptRequestQueue import RerunData
    from streamlit.ScriptRunner import RerunException
except Exception:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server

    from streamlit.script_request_queue import RerunData
    from streamlit.script_runner import RerunException


def rerun():
    """Rerun a Streamlit app from the top!"""
    widget_states = _get_widget_states()
    raise RerunException(RerunData(widget_states))


def _get_widget_states():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None
    
    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56        
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
            or
            # Streamlit >= 0.65.2
            (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')

    # Got the session object!
    try:
        state = this_session._widget_states
    except:
        # tested with Streamlit == 0.75
        state = this_session._client_state 
    return state