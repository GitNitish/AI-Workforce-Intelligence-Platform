import { useRef, useState } from 'react'
import type {
  ChangeEvent,
  FormEvent,
} from 'react'

import './EmployeeImportPage.css'
import { uploadEmployeeImport } from '../services/employees'

function EmployeeImportPage() {
  const fileInputRef =
    useRef<HTMLInputElement | null>(null)

  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [successMessage, setSuccessMessage] =
    useState<string | null>(null)
  const [errorMessage, setErrorMessage] =
    useState<string | null>(null)

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const selectedFile =
      event.target.files?.[0] ?? null

    setFile(selectedFile)
    setSuccessMessage(null)
    setErrorMessage(null)
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!file) {
      setErrorMessage(
        'Please select a CSV file first.',
      )
      return
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith('.csv')
    ) {
      setErrorMessage(
        'Only CSV files are supported.',
      )
      return
    }

    try {
      setUploading(true)
      setSuccessMessage(null)
      setErrorMessage(null)

      const result =
        await uploadEmployeeImport(file)

      setSuccessMessage(
        result.message ??
          'Employee import completed successfully.',
      )

      setFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Unable to import employees.',
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <main className="employee-import-page">
      <header className="employee-import-header">
        <span className="employee-import-eyebrow">
          ADMINISTRATION
        </span>

        <h2>Employee Import</h2>

        <p>
          Import workforce employee records
          from an approved CSV file.
        </p>
      </header>

      <section className="employee-import-card">
        <div className="employee-import-card-header">
          <h3>Upload Employee Data</h3>

          <p>
            Select a CSV file containing employee
            records. The import is validated before
            records are committed.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="employee-import-field">
            <label htmlFor="employee-import-file">
              Employee CSV
            </label>

            <input
              ref={fileInputRef}
              id="employee-import-file"
              className="employee-import-file"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>

          {file && (
            <div className="employee-import-selected">
              <span>Selected file</span>

              <strong>{file.name}</strong>
            </div>
          )}

          {successMessage && (
            <div
              className="employee-import-message success"
              role="status"
            >
              {successMessage}
            </div>
          )}

          {errorMessage && (
            <div
              className="employee-import-message error"
              role="alert"
            >
              {errorMessage}
            </div>
          )}

          <div className="employee-import-actions">
            <button
              className="employee-import-button"
              type="submit"
              disabled={!file || uploading}
            >
              {uploading
                ? 'Importing...'
                : 'Import Employees'}
            </button>
          </div>
        </form>
      </section>
    </main>
  )
}

export default EmployeeImportPage