from pptx import Presentation
from source.lyrics import SONGS
from service.function import render_song


def main():
    prs = Presentation()

    for song in SONGS:
        render_song(prs, song)

    prs.save("./PPT/setlist.pptx")


if __name__ == "__main__":
    main()
