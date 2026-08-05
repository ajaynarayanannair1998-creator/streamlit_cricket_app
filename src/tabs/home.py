import streamlit as st
from assets.styles import home_styles
STATS = [
    ("1000+", "Matches Analyzed"),
    ("19", "Seasons Covered"),
]

FEATURES = [
    {
        "title": "Single Match Data",
        "tagline": "Every match, broken down ball by ball.",
        "points": [
            "Full scorecard & result summary",
            "Player-by-player performance breakdown",
            "Run rate & score progression charts",
            "Top contenders from both sides",
        ],
    },
    {
        "title": "Stadium Analytics",
        "tagline": "Know the ground before the toss is even called.",
        "points": [
            "Typical & recent-era safe scores",
            "Toss decision trends (bat vs bowl)",
            "Toss-win → match-win success rate",
            "Team win % — who really reads this pitch",
        ],
    },
    {
        "title": "Player Analytics",
        "tagline": "Deep stats — plus an AI chatbot on call.",
        "points": [
            "Career stats: runs, 50s/100s, wickets, active years",
            "AI chatbot for custom queries & comparisons",
        ],
    },
    {
        "title": "Team Analytics",
        "tagline": "Franchise history and head-to-head rivalries.",
        "points": [
            "Overall insights of teams",
            "Top run-scorers & wicket-takers for a team",
            "Head-to-head: overall vs knockout record",
            "Next-season qualification probability",
        ],
    },
    {
        "title": "Feedback",
        "tagline": "Help shape what this project becomes.",
        "points": [
            "Tell us what's confusing or missing",
            "Suggest new stats or breakdowns you'd want",
            "Rate your overall experience",
            "Point out anything that looks off",
        ],
    },
]


def _inject_css():
    home_styles()

def _render_card(feat):
    points_html = "".join(f"<li>{p}</li>" for p in feat["points"])
    st.markdown(
        f"""
        <div class="home-feat-card">
            <div class="home-feat-title">{feat['title']}</div>
            <div class="home-feat-tagline">{feat['tagline']}</div>
            <ul class="home-feat-points">{points_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def home():
    col1,col2,col3=st.columns(3)
    """Landing/home tab. Matches the module pattern used by the other tabs
    (teams_analysis, stadium_data, player_stats, run_app, reviews) so it can
    be dropped into the same if/elif dispatch in the main file.
    """
    _inject_css()
    with col2:
        st.markdown(
            """
            <div class="home-hero-wrap">
                <div class="home-badge">Built on ball-by-ball IPL data · 2008–Present</div>
                <h1 class="home-title">IPL ANALYTICS</h1>
                <p class="home-subtitle">
                    One project, every angle. Match summaries, stadium behaviour,
                    player deep-dives with an AI analyst, and full team head-to-heads —
                    all in one place, built for people who watch cricket like it's data.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    stat_cols = st.columns([1, 3, 3, 1])
    for slot, (num, label) in zip(stat_cols[1:3], STATS):
        with slot:
            st.markdown(
                f"""
                <div class="home-stat-box">
                    <div class="home-stat-num">{num}</div>
                    <div class="home-stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="home-section-header">
            <h2>Explore the Tabs</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


    row1 = st.columns(3)
    for slot, feat in zip(row1, FEATURES[:3]):
        with slot:
            _render_card(feat)

    st.markdown('<div class="home-row-spacer"></div>', unsafe_allow_html=True)


    row2 = st.columns([1, 2, 2, 1])
    with row2[1]:
        _render_card(FEATURES[3])
    with row2[2]:
        _render_card(FEATURES[4])