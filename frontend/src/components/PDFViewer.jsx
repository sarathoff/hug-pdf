import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import { Button } from './ui/button';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const PDFViewer = ({ pdfUrl }) => {
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const onDocumentLoadSuccess = ({ numPages }) => {
        setNumPages(numPages);
        setLoading(false);
        setError(null);
    };

    const onDocumentLoadError = (error) => {
        console.error('Error loading PDF:', error);
        setError('Failed to load PDF preview');
        setLoading(false);
    };

    const goToPrevPage = () => {
        setPageNumber((prev) => Math.max(prev - 1, 1));
    };

    const goToNextPage = () => {
        setPageNumber((prev) => Math.min(prev + 1, numPages));
    };

    if (!pdfUrl) {
        return null;
    }

    return (
        <div className="w-full h-full flex flex-col items-center bg-gray-100">
            {loading && (
                <div className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-3">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                        <p className="text-sm text-gray-600">Loading PDF...</p>
                    </div>
                </div>
            )}

            {error && (
                <div className="flex items-center justify-center h-full">
                    <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
                        <p className="font-semibold text-sm">{error}</p>
                    </div>
                </div>
            )}

            <div className="flex-1 overflow-auto w-full flex justify-center py-4">
                <Document
                    file={pdfUrl}
                    onLoadSuccess={onDocumentLoadSuccess}
                    onLoadError={onDocumentLoadError}
                    loading=""
                    error=""
                    className="flex justify-center"
                >
                    <Page
                        pageNumber={pageNumber}
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                        className="shadow-2xl"
                        width={Math.min(window.innerWidth - 40, 800)}
                    />
                </Document>
            </div>

            {/* Page Navigation */}
            {numPages && numPages > 1 && (
                <div className="sticky bottom-0 w-full bg-white border-t py-3 px-4 flex items-center justify-center gap-4 shadow-lg">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={goToPrevPage}
                        disabled={pageNumber <= 1}
                        className="h-8"
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </Button>

                    <span className="text-sm font-medium text-gray-700">
                        Page {pageNumber} of {numPages}
                    </span>

                    <Button
                        variant="outline"
                        size="sm"
                        onClick={goToNextPage}
                        disabled={pageNumber >= numPages}
                        className="h-8"
                    >
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
            )}
        </div>
    );
};

export default PDFViewer;
