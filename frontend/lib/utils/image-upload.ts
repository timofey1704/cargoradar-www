interface BaseUploadResponse {
  message?: string
  [key: string]: unknown
}

export const uploadImage = async <T extends BaseUploadResponse>(
  file: File,
  endpoint: string,
  method: 'POST' | 'PATCH' = 'POST',
  fieldName: string = 'image'
): Promise<T> => {
  const formData = new FormData()
  formData.append(fieldName, file)

  const response = await fetch(endpoint, {
    method,
    body: formData,
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error(`Failed to upload image to ${endpoint}`)
  }

  return response.json()
}
