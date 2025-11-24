from supabase_client import supabase

def main():
    response = supabase.table("user").select("*").execute()

    print("ERROR:", response.error)
    print("DATA:", response.data)

if __name__ == "__main__":
    main()
