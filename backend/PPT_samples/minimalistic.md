\documentclass[aspectratio=169, 11pt]{beamer}

% --- Essential Packages ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{helvet} % The "Gold Standard" minimalist font
\usepackage{microtype} % Improves spacing and "premium" feel
\usepackage{booktabs} % For professional-grade tables
\usepackage{tikz} % For custom layouts

% --- Pure Black & White Styling ---
\setbeamercolor{background canvas}{bg=white}
\setbeamercolor{normal text}{fg=black}
\setbeamercolor{frametitle}{fg=black}
\setbeamercolor{title}{fg=black}
\setbeamercolor{structure}{fg=black}
\setbeamercolor{section in toc}{fg=black}

% --- Minimalist Frame Elements ---
\setbeamertemplate{navigation symbols}{} % Remove all icons
\setbeamertemplate{itemize items}[square] % Simple square bullets

% Custom Frametitle: Bold, Large, with a thin hairline
\setbeamertemplate{frametitle}{
\vspace{0.6cm}
{\Large\bfseries\MakeUppercase{\insertframetitle}}
\par\vskip2pt
\rule{\textwidth}{0.4pt} % Thin aesthetic hairline
}

% Custom Footer: Minimal page numbering
\setbeamertemplate{footline}{
\begin{beamercolorbox}[wd=\paperwidth, ht=1cm, dp=0.6cm, leftskip=1cm, rightskip=1cm]{footline}
\hfill
\scriptsize \insertframenumber\ /\ \inserttotalframenumber
\end{beamercolorbox}
}

% --- Custom Title Page Design ---
\setbeamertemplate{title page}{
\begin{tikzpicture}[remember picture, overlay]
% Structural Lines
\draw[line width=1.5pt] ([xshift=1cm, yshift=-2cm]current page.north west) -- ([xshift=-1cm, yshift=-2cm]current page.north east);
\draw[line width=1.5pt] ([xshift=1cm, yshift=2cm]current page.south west) -- ([xshift=-1cm, yshift=2cm]current page.south east);

        \node[anchor=west, text width=0.8\textwidth] at ([xshift=1.2cm, yshift=0.5cm]current page.west) {
            {\Huge\bfseries\MakeUppercase{\inserttitle}}\\[0.4cm]
            {\large\insertsubtitle}
        };

        \node[anchor=south west] at ([xshift=1.2cm, yshift=2.3cm]current page.south west) {
            {\small \textbf{\insertauthor} \quad | \quad \insertinstitute}
        };
    \end{tikzpicture}

}

% --- Metadata ---
\title{The Minimalist Report}
\subtitle{Standard Operating Procedure for Executive Design}
\author{Design Director}
\institute{Studio Baseline}
\date{\today}

% --- Document Starts ---
\begin{document}

% 1. Title Slide
{
\setbeamertemplate{footline}{}
\begin{frame}
\titlepage
\end{frame}
}

% 2. Table of Contents
\begin{frame}{Structure}
\vspace{1cm}
\tableofcontents
\end{frame}

\section{Design Logic}

% 3. Standard Text Slide
\begin{frame}{The Swiss Style}
\begin{itemize}
\item \textbf{High Contrast:} By removing color, we force the viewer to focus strictly on the message and the hierarchy.
\item \textbf{Typography:} Helvetica provides a neutral, yet authoritative tone.
\item \textbf{Grids:} Every element is aligned to a strict horizontal and vertical axis.
\end{itemize}

    \vspace{1cm}
    \begin{quote}
        "Design is not for philosophy, it's for life." \\
        --- Issey Miyake
    \end{quote}

\end{frame}

\section{Technical Data}

% 4. Split Layout Slide
\begin{frame}{Comparative Analysis}
\begin{columns}[T]
\column{0.45\textwidth}
\textbf{Metric Alpha}
\small
\begin{itemize}
\item Reduced cognitive load.
\item Faster processing of data.
\item Timeless aesthetic.
\end{itemize}

        \column{0.45\textwidth}
        \textbf{Metric Beta}
        \small
        \begin{itemize}
            \item Zero distraction.
            \item Professional print quality.
            \item High accessibility.
        \end{itemize}
    \end{columns}

    \vspace{1cm}
    % Minimalist Table
    \centering
    \footnotesize
    \begin{tabular}{lrr}
        \toprule
        \textbf{Component} & \textbf{Value A} & \textbf{Value B} \\
        \midrule
        Structure & 100 & 85 \\
        Hierarchy & 94 & 100 \\
        \bottomrule
    \end{tabular}

\end{frame}

% 5. Inverted "Impact" Slide (The only "Premium" variation)
{
\setbeamercolor{background canvas}{bg=black}
\setbeamercolor{normal text}{fg=white}
\begin{frame}
\centering
\vspace{2.5cm}
{\color{white}\Huge\bfseries BOLD STATEMENTS\\ REQUIRE SPACE.}
\end{frame}
}

% 6. Closing Slide
\begin{frame}
\centering
\vspace{2cm}
{\large\bfseries QUESTIONS} \\
\vspace{0.5cm}
\rule{20pt}{1pt} \\
\vspace{0.5cm}
\small \texttt{contact@studio-baseline.com}
\end{frame}

\end{document}
