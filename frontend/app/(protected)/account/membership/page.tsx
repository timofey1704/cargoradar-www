'use client'

import { useGetMembershipInfo } from '@/hooks/use-membership-actions'
import MembershipView from '@/components/account/membership/membership-view'

const MembershipPage = () => {
  const { data, isLoading, isError } = useGetMembershipInfo('client')
  return <MembershipView membershipInfo={data} isLoading={isLoading} isError={isError} />
}

export default MembershipPage
