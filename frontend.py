import streamlit as st
import grpc
import proto.story_pb2 as story_pb2
import proto.story_pb2_grpc as story_pb2_grpc

# gRPC server address
GRPC_SERVER_ADDRESS = "localhost:50052"

# Dropdown options
regions = ["PK", "US", "UK"]
themes = ["Inspirational", "Humorous", "Informative", "Dramatic", "Comedy", "Sarcasm", "Satire", "Parody", "Romantic", "Suspense", "Thriller", "Horror", "Adventure", "Fantasy", "Science Fiction", "Historical Fiction", "Cruelty", "Tragedy", "Mystery", "Detective", "Supernatural", "Magical Realism", "Realism", "Surrealism", "Absurdism", "Dystopian", "Utopian", "Cyberpunk", "Steampunk", "Post-Apocalyptic"]

# Streamlit UI
st.title("Trend Story Generator")
st.write("Generate a story based on your selected region, theme, and trend.")

# Dropdowns
selected_region = st.selectbox("Select Region", regions)

# Fetch trends based on the selected region
if st.button("Fetch Trends"):
    try:
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
            stub = story_pb2_grpc.StoryServiceStub(channel)
            request = story_pb2.TrendsRequest(region=selected_region)
            response = stub.GetTrends(request)
            if response.status == "success":
                trends = response.trends  # Convert to list for display
                st.session_state["trends"] = trends  # Store trends in session state
                st.success("Trends fetched successfully!")
            else:
                st.error(f"Error: {response.status}")
    except Exception as e:
        st.error(f"Failed to connect to the server: {e}")

# Display trends dropdown if trends are fetched
if "trends" in st.session_state:
    selected_trend = st.selectbox("Select Trend", list(st.session_state["trends"]))
    selected_theme = st.selectbox("Select Theme", themes)
    print(type(themes))
    print(type(st.session_state["trends"]))

    # Generate Story Button
    if st.button("Generate Story"):
        try:
            with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
                stub = story_pb2_grpc.StoryServiceStub(channel)
                request = story_pb2.StoryRequest(
                    region=selected_region,
                    theme=selected_theme,
                    topic=selected_trend
                )
                response = stub.GenerateStory(request)
                if response.status == "success":
                    st.subheader("Generated Story")
                    st.write(response.story)
                    st.subheader("Trending Searches")
                    st.write(response.trends)
                else:
                    st.error(f"Error: {response.status}")
        except Exception as e:
            st.error(f"Failed to connect to the server: {e}")