import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import apiClient from "../api/client";


type DocumentItem = {
  id: number;
  filename: string;
  filepath: string;
  user_id: number;
  uploaded_at: string;
};


type AskResponse = {
  question: string;
  answer: string;
  retrieved_chunks: string[];
};


function getErrorMessage(
  error: unknown,
  fallback: string,
) {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail ?? fallback;
  }

  return fallback;
}


function DashboardPage() {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<
    DocumentItem[]
  >([]);
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [isLoadingDocuments, setIsLoadingDocuments] =
    useState(true);
  const [isUploading, setIsUploading] =
    useState(false);
  const [isAsking, setIsAsking] = useState(false);


  async function loadDocuments() {
    try {
      setIsLoadingDocuments(true);

      const response = await apiClient.get<
        DocumentItem[]
      >("/documents/");

      setDocuments(response.data);
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Could not load your documents.",
        ),
      );
    } finally {
      setIsLoadingDocuments(false);
    }
  }


  useEffect(() => {
    void loadDocuments();
  }, []);


  async function handleUpload(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Select a PDF before uploading.");
      return;
    }

    setError("");
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await apiClient.post(
        "/documents/upload",
        formData,
      );

      setSelectedFile(null);

      const fileInput = document.getElementById(
        "pdf-file",
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = "";
      }

      await loadDocuments();
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "The PDF could not be uploaded.",
        ),
      );
    } finally {
      setIsUploading(false);
    }
  }


  async function handleDelete(documentId: number) {
    const shouldDelete = window.confirm(
      "Delete this document and its indexed data?",
    );

    if (!shouldDelete) {
      return;
    }

    setError("");

    try {
      await apiClient.delete(
        `/documents/${documentId}`,
      );

      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (documentItem) =>
            documentItem.id !== documentId,
        ),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "The document could not be deleted.",
        ),
      );
    }
  }


  async function handleAsk(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
      return;
    }

    setError("");
    setAnswer("");
    setIsAsking(true);

    try {
      const response =
        await apiClient.post<AskResponse>(
          "/rag/ask",
          {
            question: cleanQuestion,
          },
        );

      setAnswer(response.data.answer);
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "The question could not be processed.",
        ),
      );
    } finally {
      setIsAsking(false);
    }
  }


  function handleLogout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }


  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div className="brand dashboard-brand">
          <span className="brand-icon">AI</span>

          <div>
            <h1>Document Search</h1>
            <p>Secure AI-powered PDF search</p>
          </div>
        </div>

        <button
          className="secondary-button"
          onClick={handleLogout}
        >
          Log out
        </button>
      </header>

      <section className="dashboard-intro">
        <div>
          <span className="eyebrow">
            YOUR KNOWLEDGE WORKSPACE
          </span>

          <h2>
            Ask questions.
            <br />
            Find answers instantly.
          </h2>

          <p>
            Upload PDFs and receive answers grounded
            only in your private documents.
          </p>
        </div>

        <form
          className="upload-card"
          onSubmit={handleUpload}
        >
          <div className="upload-icon">PDF</div>

          <div>
            <h3>Upload a document</h3>
            <p>PDF only, up to 10 MB</p>
          </div>

          <input
            id="pdf-file"
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) =>
              setSelectedFile(
                event.target.files?.[0] ?? null,
              )
            }
          />

          {selectedFile && (
            <span className="selected-file">
              {selectedFile.name}
            </span>
          )}

          <button
            type="submit"
            disabled={isUploading}
          >
            {isUploading
              ? "Uploading..."
              : "Upload PDF"}
          </button>
        </form>
      </section>

      {error && (
        <p className="dashboard-error">{error}</p>
      )}

      <section className="dashboard-grid">
        <article className="panel documents-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">
                DOCUMENT LIBRARY
              </span>
              <h3>Your documents</h3>
            </div>

            <span className="document-count">
              {documents.length}
            </span>
          </div>

          {isLoadingDocuments ? (
            <p className="empty-state">
              Loading documents...
            </p>
          ) : documents.length === 0 ? (
            <p className="empty-state">
              Upload your first PDF to begin.
            </p>
          ) : (
            <div className="document-list">
              {documents.map((documentItem) => (
                <div
                  className="document-row"
                  key={documentItem.id}
                >
                  <span className="file-badge">
                    PDF
                  </span>

                  <div className="document-info">
                    <strong>
                      {documentItem.filename}
                    </strong>
                    <span>
                      Document #{documentItem.id}
                    </span>
                  </div>

                  <button
                    className="delete-button"
                    onClick={() =>
                      void handleDelete(
                        documentItem.id,
                      )
                    }
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="panel chat-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">
                AI ASSISTANT
              </span>
              <h3>Ask your documents</h3>
            </div>

            <span className="online-status">
              Online
            </span>
          </div>

          <div className="answer-area">
            {answer ? (
              <div className="answer-card">
                <span>Answer</span>
                <p>{answer}</p>
              </div>
            ) : (
              <div className="empty-answer">
                <div className="answer-icon">AI</div>
                <p>
                  Ask a question about your uploaded
                  PDFs.
                </p>
              </div>
            )}
          </div>

          <form
            className="question-form"
            onSubmit={handleAsk}
          >
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="What would you like to know?"
              rows={3}
              maxLength={1000}
              required
            />

            <button
              type="submit"
              disabled={
                isAsking || documents.length === 0
              }
            >
              {isAsking
                ? "Searching..."
                : "Ask AI"}
            </button>
          </form>
        </article>
      </section>
    </main>
  );
}


export default DashboardPage;