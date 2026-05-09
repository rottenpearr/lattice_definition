from mp_api.client import MPRester

with MPRester(api_key="EksD5qbZQUnFzqh5twm8kbUV9xcbu7YQ") as mpr:
    data = mpr.materials.search(material_ids=["mp-2625"])
