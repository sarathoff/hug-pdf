% Copyright (c) 2022 by Lars Spreng
% This work is licensed under the Creative Commons Attribution 4.0 International License.
% To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% You can add your packages and commands to the loadslides.tex file.
% The files in the folder "styles" can be modified to change the layout and design of your slides.
% I have included examples on how to use the template below.
% Some of these examples are taken from the Metropolis template.
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

\documentclass[
11pt,notheorems,hyperref={pdfauthor=whatever}
]{beamer}

\input{loadslides.tex} % Loads packages and some defined commands

\title[
% Text entered here will appear in the bottom middle
]{Presentation Title}

\subtitle{Presentation Subtitle}

\author[
% Text entered here will appear in the bottom left corner
]{
John Doe
}

\institute{
Author Affiliation, \\
University of Author}
\date{\today}

\begin{document}

% Generate title page
{
\setbeamertemplate{footline}{}
\begin{frame}
\titlepage
\end{frame}
}
\addtocounter{framenumber}{-1}

% You can declare different parts as a parentof sections
\begin{frame}{Part I: Demo Presentation Part}
\tableofcontents[part=1]
\end{frame}
\begin{frame}{Part II: Demo Presentation Part 2}
\tableofcontents[part=2]
\end{frame}

\makepart{Demo Part}

\section{Introduction}
\begin{frame}
\begin{itemize}
\item This template provides an elegant and minimalistic layout for beamer slides. Hence the name \emphasize{\textbf{Elegant Slides}}.
\item I created Elegant Slides because I wasn't satisfied with any of the existing Beamer templates, which look slightly different than Elegant Slides.
\item My goal was to create a layout that is \alert{\textbf{simplistic but beautiful}} and focuses on the content, rather than crowding each slide with lots of different coloured boxes.
\item I designed Elegant Slides for \example{\textbf{lecture notes and technical presentations}} but it can be used for any kind of talk.
\end{itemize}
\end{frame}

\subsection{Colors}
\begin{frame}[fragile]
\centering
The template provides different color themes.\\
Set \verb+\usetheme[style=lecture]{elegant}+ in loadslides.tex\\[0.8cm]
\newcommand{\colorRow}[1]{
\begin{tabular}{p{4cm}cccc}
#1 & \cellcolor{primary}\hspace*{1cm} &\cellcolor{secondary}\hspace*{1cm}&\cellcolor{tertiary}\hspace\*{1cm}\\
\end{tabular}
}
\colorRow{Lecture}\\[0.3cm]
\definecolor{primary}{HTML}{08457E}
\definecolor{secondary}{HTML}{B8860B}
\definecolor{tertiary}{HTML}{B22222}
\colorRow{Gold}\\[0.3cm]
\definecolor{primary}{HTML}{08457E}
\definecolor{secondary}{HTML}{B02A30}
\definecolor{tertiary}{HTML}{006400}
\colorRow{Red}\\[0.3cm]
\definecolor{primary}{HTML}{08457E}
\definecolor{secondary}{HTML}{CC5500}
\definecolor{tertiary}{HTML}{008B8B}
\colorRow{Orange}\\[0.3cm]
\definecolor{primary}{HTML}{08457E}
\definecolor{secondary}{HTML}{E60073}
\definecolor{tertiary}{HTML}{33CCCC}
\colorRow{Gray}\\[0.3cm]

\centering Gray is a slightly more subtle version of the default \textit{Lecture} theme with gray, rather than pink, subtitles.
\end{frame}

\subsection{Frames}
\begin{frame}
Unless the user enters their own custom frame titles and subtitles, Elegant Slides automatically inserts the section title and, if specified, the subsection title as frame titles and frame subtitles.
\end{frame}

\begin{frame}{}{Custom Subsection}
This frame has a custom subtitle. The frame title is automatically inserted and corresponds to the section title.
\end{frame}

\begin{frame}{Custom Title}{Custom Subsection with Footnote}
This frame has a custom title and a custom subtitle.\footnote{This is a footnote. See also \citet{example_2022}. }
\end{frame}

\subsection{Fonts}
\begin{frame}[fragile]
\begin{itemize}
\item Font types can be changed in loadslides.tex.
\item For lecture notes or reports, the \textit{Lecture} theme together with \verb +\RequirePackage{palatino}+ and \verb+\usefonttheme{serif}+ works well.
\item For talks and other presentations, \verb+\RequirePackage[scaled]{helvet}+ with any of the other themes, such as \textit{Gold}, works better.
\item Text can be highlighted as follows:
\begin{itemize}
\item Regular
\item \emphasize{Emphasize}
\item \alert{Alert}
\item \example{Example}
\item \textit{Italic}
\item \textbf{Bold}
\end{itemize}
\end{itemize}

\end{frame}

\subsection{Lists}

\begin{frame}
\begin{columns}[T,onlytextwidth]
\column{0.33\textwidth}
\textbf{Items}
\begin{itemize}
\item Cats
\begin{itemize}
\item British Shorthair
\end{itemize}
\item Dogs \item Birds
\end{itemize}

    \column{0.33\textwidth}
      \textbf{Enumerations}
      \begin{enumerate}
        \item First
        \begin{enumerate}
            \item First subpoint
        \end{enumerate}
        \item Second \item Last
      \end{enumerate}

    \column{0.33\textwidth}
      \textbf{Descriptions}
      \begin{description}
        \item[Apples] Yes \item[Oranges] No \item[Grappes] No
      \end{description}

\end{columns}
\end{frame}

\subsection{Table}
\begin{frame}
\begin{table}
\caption{Largest cities in the world (source: Wikipedia)}
\begin{tabular}{@{} lr @{}}
\toprule
City & Population\\
\midrule
Mexico City & 20,116,842\\
Shanghai & 19,210,000\\
Peking & 15,796,450\\
Istanbul & 14,160,467\\
\bottomrule
\end{tabular}
\hspace\*{1cm}
\setlength\extrarowheight{3pt}
\begin{tabular}{|lr|}
\hline
\rowcolor{primary}\color{white}City & \color{white}Population\\
\hline
Mexico City & 20,116,842\\
Shanghai & 19,210,000\\
Peking & 15,796,450\\
Istanbul & 14,160,467\\
\hline
\end{tabular}
\end{table}
\end{frame}

\subsection{Figures}
\begin{frame}
\begin{figure}[htbp]
\centering
\caption{Plot of $y=x^2$}
\begin{tikzpicture}
\begin{axis}[
legend columns=3,
legend style={at={(0.5,-0.3)},anchor=north},
width = \textwidth,
height = 2.5in,
xmin = -3,
xmax = 3,
ymin = 0,
ymax = 10,
]
\addplot[primary] {x^2};
\addlegendentry{$x^2$}
\end{axis}
\end{tikzpicture}
\end{figure}

\end{frame}

\subsection{Blocks}
\begin{frame}

\centering
\begin{minipage}[b]{0.5\textwidth}

      \begin{block}{Default}
        Block content.
      \end{block}

      \begin{alertblock}{Alert}
        Block content.
      \end{alertblock}

      \begin{exampleblock}{Example}
        Block content.
      \end{exampleblock}

    \end{minipage}

\end{frame}

\section{Maths}
\subsection{Equations}
\begin{frame}
\begin{itemize}
\item A numbered equation:
\begin{equation}
y_t = \beta x_t + \varepsilon_t
\end{equation}
\item Another equation:
\begin{equation*}
\mathbf{Y} = \boldsymbol{\beta} \mathbf{X} + \boldsymbol{\varepsilon}\_t
\end{equation*}
\end{itemize}
\end{frame}

\subsection{Theorem}
\begin{frame}
\begin{itemize}
\item Theorems are numbered consecutively.
\end{itemize}
\begin{theorem}[Example Theorem]
Given a discrete random variable X, which takes values in the alphabet $\mathcal{X}$ and is distributed according to $p:{\mathcal {X}}\to [0,1]$:
\begin{equation}
\mathrm {H} (X):=-\sum \_{x\in {\mathcal {X}}}p(x)\log p(x)=\mathbb {E} [-\log p(X)]
\end{equation}
\end{theorem}
\end{frame}

\begin{frame}{}{Definitions}
\begin{itemize}
\item Definition numbers are prefixed by the section number in the respective part.
\end{itemize}
\begin{definition}[Example Definition]
Given a discrete random variable X, which takes values in the alphabet $\mathcal{X}$ and is distributed according to $p:{\mathcal {X}}\to [0,1]$:
\begin{equation}
\mathrm {H} (X):=-\sum \_{x\in {\mathcal {X}}}p(x)\log p(x)=\mathbb {E} [-\log p(X)]
\end{equation}
\end{definition}
\end{frame}

\begin{frame}{}{Examples}
\begin{itemize}
\item Examples are numbered as definitions.
\end{itemize}
\begin{examp}[Example Theorem]
Given a discrete random variable X, which takes values in the alphabet $\mathcal{X}$ and is distributed according to $p:{\mathcal {X}}\to [0,1]$:
\begin{equation}
\mathrm {H} (X):=-\sum \_{x\in {\mathcal {X}}}p(x)\log p(x)=\mathbb {E} [-\log p(X)]
\end{equation}
\end{examp}
\end{frame}

\makepart{Demo Presentation Part 2}

\section{Section}
\subsection{Subsection}
\subsubsection{Subsubsection}
\subsubsection{Subsubsection}
\subsection{Subsection}
\subsubsection{Subsubsection}
\subsubsection{Subsubsection}
\section{Section}
\subsection{Subsection}
\subsubsection{Subsubsection}
\subsubsection{Subsubsection}
\subsection{Subsection}
\subsubsection{Subsubsection}
\subsubsection{Subsubsection}

\begin{frame}[allowframebreaks]{References}
\printbibliography
\end{frame}
\end{document}
