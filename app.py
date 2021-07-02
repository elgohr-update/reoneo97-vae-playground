import streamlit as st
from streamlit_drawable_canvas import st_canvas
import os
import app_utils as utils
from PIL import Image

st.set_page_config("VAE Playground")
st.title("🎮 VAE Playground")
title_img = Image.open("images/title_img.png")

st.image(title_img)
st.markdown(
    "This is a simple streamlit app to showcase how different VAEs "
    "function and how the differences in architecture and "
    "hyperparameters will show up in the generated images. \n \n"
    "In this playground there will be two scenarios that you can use to "
    "interact with the models:"
)
st.markdown(
    """
    1. **Image Reconstruction:** <br>
    Observe quality of image reconstruction
    2. **Image Interpolation:** <br>
    Sample images equally spaced between 2 drawn images. Observe tradeoff
    between image reconstruction and latents space regularity
    """, unsafe_allow_html=True
)

#  the first is a reconstruction one which is "
# "used to look at the quality of image reconstruction. The second one is "
# "interpolation where you can generate intermediary data points between "
# "two images. From here this you can analyze the regularity of the latent "
# "distribution."

st.markdown(
    "There are also two different architectures. The first one is the vanilla "
    "VAE and the other is the convolutional VAE which uses convolutional layers"
    " for the encoder and decoder. "
    "To find out more check this accompanying"
    " [blogpost](https://towardsdatascience.com/beginner-guide-to-variational-autoencoders-vae-with-pytorch-lightning-13dbc559ba4b)"
)
st.subheader("Hyperparameters:")
st.markdown(
    "- **alpha**: Weight for reconstruction loss, higher values will lead to better"
    "image reconstruction but possibly poorer generation \n"
    "- **dim**: Hidden Dimension of the model."
)


def load_model_files():
    files = os.listdir("./saved_models/")
    # Docker creates some whiteout files which mig
    files = [i for i in files if ".ckpt" in i]
    clean_names = [utils.parse_model_file_name(name) for name in files]
    return {k: v for k, v in zip(clean_names, files)}


file_name_map = load_model_files()
files = list(file_name_map.keys())

st.header("🖼️ Image Reconstruction", "recon")

with st.form("reconstruction"):
    model_name = st.selectbox("Choose Model:", files,
                              key="recon_model_select")
    recon_model_name = file_name_map[model_name]
    recon_canvas = st_canvas(
        # Fixed fill color with some opacity
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=8,
        stroke_color="#FFFFFF",
        background_color="#000000",
        update_streamlit=True,
        height=150,
        width=150,
        drawing_mode="freedraw",
        key="recon_canvas",
    )
    submit = st.form_submit_button("Perform Reconstruction")
    if submit:
        recon_model = utils.load_model(recon_model_name)
        inp_tens = utils.canvas_to_tensor(recon_canvas)
        _, _, out = recon_model(inp_tens)
        out = (out+1)/2
        out_img = utils.resize_img(utils.tensor_to_img(out), 150, 150)
if submit:
    st.image(out_img)


st.header("🔍 Image Interpolation", "interpolate")
with st.form("interpolation"):
    model_name = st.selectbox("Choose Model:", files)
    inter_model_name = file_name_map[model_name]
    stroke_width = 8
    cols = st.beta_columns([1, 3, 2, 3, 1])

    with cols[1]:
        canvas_result_1 = st_canvas(
            # Fixed fill color with some opacity
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#FFFFFF",
            background_color="#000000",
            update_streamlit=True,
            height=150,
            width=150,
            drawing_mode="freedraw",
            key="canvas1",
        )

    with cols[3]:
        canvas_result_2 = st_canvas(
            # Fixed fill color with some opacity
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#FFFFFF",
            background_color="#000000",
            update_streamlit=True,
            height=150,
            width=150,
            drawing_mode="freedraw",
            key="canvas2",
        )
    submit = st.form_submit_button("Perform Interpolation")
    if submit:
        inter_model = utils.load_model(inter_model_name)
        inter_tens1 = utils.canvas_to_tensor(canvas_result_1)
        inter_tens2 = utils.canvas_to_tensor(canvas_result_2)
        inter_output = utils.perform_interpolation(
            inter_model, inter_tens1, inter_tens2
        )
if submit:
    st.image(inter_output)

st.write(
    """
    ## 💡 Interesting Note:
    At low values of alpha, we can see the phenomenon known as the **posterior
    collapse**. This is when the loss function does not weight reconstruction 
    quality sufficiently and the reconstructed images look like digits but 
    nothing like the input.

    Essentially what happens is that the encoder encodes data points to a 
    random gaussian distribution (to minimize KL Loss) but this does not give 
    sufficient information to the decoder. In this case our decoder behaves 
    very similarly to a Generative Adversarial Network (GAN) which generates 
    images from random noise. 
    """
)
