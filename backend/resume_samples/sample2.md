\documentclass[letterpaper,11pt]{article}

% Choose bibliography style for formatting list of publications
\usepackage[style=ieee,url=false,doi=false,maxbibnames=99,sorting=ydnt,dashed=false]{biblatex}
\bibliography{papers}

% Choose theme, e.g. black, RedViolet, ForestGreen, MidnightBlue
\def\theme{MidnightBlue}

% More predefined colors can be found in
% https://en.wikibooks.org/wiki/LaTeX/Colors
% Example photograph taken from Wikimedia Commons
% https://commons.wikimedia.org/wiki/File:Kiara_Krit_passport.jpg

\usepackage{simplecv}

\boldname{Surname}{Name}{N.}

\begin{document}

% Heading
\headinginline{Name Surname}{
Website: \website{example.com} \\
Email: \email{example@example.edu} \\
LinkedIn: \linkedin{name-surname} \\
GitHub: \github{example}
}

% \headingphoto{Name Surname}{
% Website: \website{example.com} \\
% Email: \email{example@example.edu} \\
% LinkedIn: \linkedin{name-surname} \\
% GitHub: \github{example}
% }{photo.jpg}

% Page One
\import{sections/}{education.tex}
\import{sections/}{experience.tex}
\import{sections/}{publications.tex}

\pagebreak

% Page Two
\import{sections/}{teaching.tex}
\sidebyside
{\import{sections/}{skills.tex}}
{\import{sections/}{languages.tex}}
\import{sections/}{projects.tex}
\import{sections/}{awards.tex}
\import{sections/}{extracurricular.tex}

\end{document}
