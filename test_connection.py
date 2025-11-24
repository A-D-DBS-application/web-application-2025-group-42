from supabase_client import supabase

def main():
    response = supabase.table("user").select("*").execute()

    print("RESPONSE:", response)
    print("TYPE:", type(response))

    # Probeer bekende properties
    try:
        print("DATA:", response.data)
    except:
        print("No attribute: data")

    try:
        print("ERROR:", response.error)
    except:
        print("No attribute: error")

    try:
        print("DICT:", response.dict())
    except:
        print("No dict()")

if __name__ == "__main__":
    main()
