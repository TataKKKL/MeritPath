import type { User } from '@supabase/supabase-js'
import type { GetServerSidePropsContext } from 'next'
import Link from 'next/link'
import { createClient } from '@/utils/supabase/server-props'

type HomeProps = {
  user: User | null
}

const Home = ({ user }: HomeProps) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900 p-8">
      <h1 className="text-black dark:text-white text-4xl mb-8">Welcome to the MeritPath App</h1>
      
      {user ? (
        <div className="text-center">
          <p className="text-black dark:text-white text-xl mb-4">
            Logged in as: {user.email}
          </p>
        </div>
      ) : (
        <div className="text-center">
          <Link 
            href="/login" 
            className="inline-block px-6 py-3 text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Log In
          </Link>
        </div>
      )}
    </div>
  );
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const supabase = createClient(context)
  const { data: { user }, error } = await supabase.auth.getUser()
  
  if (error) {
    console.error('Error fetching user:', error)
    return {
      props: {
        user: null,
        error: error.message,
      },
    }
  }
  
  return {
    props: {
      user: user || null,
    },
  }
}

export default Home;