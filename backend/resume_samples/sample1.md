\documentclass{resume} % Use the custom resume.cls style
\usepackage[dvipsnames]{xcolor}
\usepackage{hyperref}
\usepackage[backend=biber, style=ieee, sorting=none]{biblatex}
\addbibresource{references.bib}

\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.1in]{geometry} % Document margins
\newcommand{\tab}[1]{\hspace{.2667\textwidth}\rlap{#1}}
\newcommand{\itab}[1]{\hspace{0em}\rlap{#1}}
\name{Andrew Carnegie} % Your name
\address{Homepage: \href{https://users.ece.cmu.edu/~example/}{\texttt{users.ece.cmu.edu/\textasciitilde name}}}
\address{
\href{https://scholar.google.com/example}{Google Scholar} \\
\href{https://github.com/example}{Github} \\
\href{https://www.linkedin.com/in/example/}{LinkedIn}
}
\address{Phone: (+1) 412-123-4567 \\ Email: \texttt{name@andrew.cmu.edu}} % Your phone number and email

\definecolor{CarnegieMellonRed}{RGB}{196,18,48}

\renewenvironment{rSection}[1]{
\sectionskip
\textcolor{CarnegieMellonRed}{\MakeUppercase{#1}}
\sectionlineskip
\hrule
\begin{list}{}{
\setlength{\leftmargin}{1.5em}
}
\item[]
}{
\end{list}
}

\begin{document}
\begin{rSection}{Education}
{\bf Carnegie Mellon University (CMU)} \hfill {\em May 2025 (expected)}
\\ M.S. in Electrical and Computer Engineering (Advanced Study)\hfill
\\ GPA: 4.0/4.0 \hfill
\\ \textit{Related courses: A, B, C. }

{\bf Huazhong University of Science and Technology (HUST)} \hfill {\em June 2023}
\\ B.E. in Automation (Advanced Class)
\\ \qquad GPA: 3.9/4.0\qquad \hfill
\\ \textit{Related courses: A, B, C.
}

\end{rSection}

\begin{rSection}{Research Interests}
I am interested in A and B.
\end{rSection}

\begin{rSection}{Research Experience}
\begin{rSubsection}{Project name 1 \cite{paper1}}{Jan 2024 - Present}{Supervisors: \href{https://example.com/}{Dr. A}, \href{https://example.com/}{Prof. B}, and \href{https://example.com/}{Prof. C}}{CMU}
\item Proposed ...
\item Found ...
\item Completed ...
\item Modified ...
\item Proposed ...
\item Finished ...
\end{rSubsection}

\begin{rSubsection}{Project name 2 \cite{paper2}}{Dec 2023 - Feb 2024}{Supervisors: \href{https://example.weebly.com/}{Dr. A} and \href{https://www.ece.cmu.edu/directory/bios/example}{Prof. B}}{CMU}
\item Ran experiments for ...
\item Organized ...
\item Explored ...
\item Proposed ...
\item Finished ...
\end{rSubsection}
\end{rSection}

\begin{rSection}{Publications} \itemsep -2pt

\leavevmode\printbibliography[heading=none]

\end{rSection}
\newpage
\begin{rSection}{Achievements} \itemsep -2pt
{Scholarship, awarded by xxx}\hfill {\em Summer 2023} \\
{Scholarship, awarded by xxx}\hfill {\em Fall 2022} \\
{Scholarship, awarded by xxx} \hfill {\em Summer 2022} \\
{Scholarship, awarded by xxx}\hfill {\em Fall 2019}
\end{rSection}

\begin{rSection}{Skills/Hobbies} \itemsep -2pt
\begin{tabular}{ @{} >{\bfseries}l @{\hspace{6ex}} l }
Programming Languages & Python, C/C++, MATLAB, HTML \\
Machine Learning Tools & Pytorch, Tensorflow, Sklearn, Pandas, Numpy \\
Hobbies & birding and hiking \\
\end{tabular}
\end{rSection}
\end{document}
