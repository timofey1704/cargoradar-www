'use client'

import { useGetMembershipInfo } from '@/hooks/use-membership-actions'
import MembershipView from '@/components/account/membership/membership-view'

const ExecutorMembershipPage = () => {
  const { data, isLoading, isError } = useGetMembershipInfo('executor')
  return <MembershipView membershipInfo={data} isLoading={isLoading} isError={isError} />
}

export default ExecutorMembershipPage
