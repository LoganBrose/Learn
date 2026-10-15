# Daily Learn

A static website that teaches one new topic every day: a short lesson, teach-back questions, a 5-question quiz, and ideas to go deeper.

Open `index.html` in a browser, or host the folder on GitHub Pages (Settings → Pages → Deploy from branch `main`, folder `/ (root)`).

## How it works
- The topic is chosen the first time you open the site each day and stays until midnight. Categories rotate, and no topic repeats until all have been shown.
- Progress (streak, finished quizzes, teach-back notes) is saved in your browser only.

## Files
- `index.html`: the whole app.
- `lessons/manifest.js`: the list of every lesson (id, title, category, chunk number).
- `lessons/lessons-NN.js`: full lesson content, loaded on demand.
- `tools/validate.py`: optional checker for lesson files (`python3 tools/validate.py`).

## Adding lessons
Add a new `lessons/lessons-NN.js` file and append its entries to `lessons/manifest.js`. New lessons join the rotation automatically, and past days keep their topics.
