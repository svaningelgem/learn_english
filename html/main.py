from pathlib import Path

import pandas as pd
import streamlit as st


video_path = (Path(__file__).parent / 'videos').resolve().absolute()


@st.cache_data(show_spinner=False)
def load_data():
    name = []
    img = []
    movie = []

    for json in video_path.rglob('*.json'):
        video = image = None

        for other in json.parent.glob(json.stem + '.*'):
            if other.suffix == '.json':
                continue
            if other.suffix.lower() == '.mp4':
                video = other
            elif other.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                image = other
            else:
                raise ValueError(f"Invalid file? ({other})")

        if video and image:
            name.append(image.stem[9:])
            img.append(str(image))
            movie.append(str(video))

    return (
        pd.DataFrame({'name': name, 'img': img, 'movie': movie})
        .sort_values(by='img', ascending=False, ignore_index=True)
    )


@st.cache_data(show_spinner=False)
def split_frame(input_df):
    return [input_df.loc[i : i + 20 - 1, :].reset_index() for i in range(0, len(input_df), 20)]


rows = 20
data = load_data()


total_pages = (
    int(len(data) / rows) if int(len(data) / rows) > 0 else 1
)

current_page = st.sidebar.number_input(
    "Page", min_value=1, max_value=total_pages, step=1
)

st.sidebar.markdown(f"Page **{current_page}** of **{total_pages}** ")


pages = split_frame(data)
to_show = pages[current_page - 1]
rows = min(rows, len(to_show))

txt = """
# Words
"""
for i in range(rows):
    word = to_show.name[i]
    if not word:
        continue

    txt += f"- [{word}](#word_{i})\n"

st.sidebar.markdown(txt)


with st.container():
    for i in range(rows):
        div = st.container()
        with div:
            st.header(to_show.name[i], anchor=f'word_{i}')
            st.video(str(Path(to_show.movie[i]).relative_to(video_path.parent)).replace('\\', '/'))
