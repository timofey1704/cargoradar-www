import { useRouter } from 'next/navigation'
import { IoExitOutline } from 'react-icons/io5'
import useClientStore from '@/store/clientStore'
import { Button } from '../ui/button'

const Logout = () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/logout/`, {
        method: 'POST',
        credentials: 'include',
      })

      useClientStore.getState().logout()

      router.replace('/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <Button
      defaultText="Выйти из аккаунта"
      className="flex w-full items-center rounded-lg px-4 py-4 font-medium text-gray-600 transition-colors hover:bg-gray-100"
      size="sm"
      onClick={handleLogout}
    />
  )
}

export default Logout
