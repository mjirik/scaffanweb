from loguru import logger
from pathlib import Path
import numpy as np
from .models import ServerDataFileName, LobuleCoordinates, ExampleData
from .models import get_output_dir
import os.path as op
from scaffanweb import settings
from microimprocessing import scaffanweb_tools, models

# report generator
def create_html_report(user):
    html_report = 'We had a great quarter!'
    logger.debug(html_report)
    return html_report


def make_thumbnail(serverfile:ServerDataFileName):
    import scaffan
    import scaffan.algorithm
    import scaffan.image
    logger.debug(f"serverfile={serverfile}")

    nm = str(Path(serverfile.imagefile.path).name)
    anim = scaffan.image.AnnotatedImage(serverfile.imagefile.path)


    full_view = anim.get_view(
        location=[0, 0], level=0, size_on_level=anim.get_slide_size()[::-1]
    )
    # pxsz_mm = float(self.get_parameter("Processing;Preview Pixelsize")) * 1000
    pxsz_mm = 0.02
    view_corner = full_view.to_pixelsize(pixelsize_mm=[pxsz_mm, pxsz_mm])
    img = view_corner.get_region_image(as_gray=False)
    pth = str(Path(settings.MEDIA_ROOT) / (nm + ".preview.jpg"))
    # pth = serverfile.outputdir + nm + ".preview.jpg"

    # pth = serverfile.imagefile.path + ".thumbnail.jpg"
    logger.debug("thumbnail path")
    logger.debug(pth)
    pth_rel = op.relpath(pth, settings.MEDIA_ROOT)
    logger.debug(pth_rel)
    serverfile.preview = pth_rel
    serverfile.preview_pixelsize_mm = pxsz_mm
    import skimage.io
    logger.debug(f"img max: {np.max(img)}, img.dtype={img.dtype}")
    if img.dtype != np.uint8:
        img = (img*255).astype(np.uint8)
    skimage.io.imsave(pth, img[:,:,:3])

    serverfile.save()

def run_processing(serverfile:ServerDataFileName):
    import scaffan
    import scaffan.algorithm
    import scaffan.image
    coords = LobuleCoordinates.objects.filter(server_datafile=serverfile)

    centers_mm = [[coord.x_mm, coord.y_mm] for coord in coords]

    logger.debug(coords)
    # serverfile.outputdir = get_output_dir()
    # serverfile.process_started = True
    serverfile.save()

    # cli_params = [
    #     settings.CONDA_EXECUTABLE, "run", "-n", "scaffanweb", "python", "-m", "scaffan", "-lf",
    #     str(Path(serverfile.outputdir) / 'scaffan.log'), "nogui",
    #     "-i", str(serverfile.imagefile.path),
    #     "-o", str(serverfile.outputdir),
    # ]
    # for coord in coords:
    #     cli_params.append("--seeds_mm")
    #     cli_params.append(str(coord.x_mm))
    #     cli_params.append(str(coord.y_mm))
    #
    # logger.debug(f"adding task to queue CLI params: {' '.join(cli_params)}")


    logger.debug("Scaffan processing init")
    mainapp = scaffan.algorithm.Scaffan()
    mainapp.set_input_file(serverfile.imagefile.path)
    mainapp.set_output_dir(serverfile.outputdir)
    fn,_,_ = models.get_common_spreadsheet_file(serverfile.owner)
    mainapp.set_common_spreadsheet_file(str(fn).replace("\\", "/"))
    # settings.SECRET_KEY
    logger.debug("Scaffan processing run")
    if len(centers_mm) > 0:
        mainapp.set_parameter("Input;Lobulus Selection Method", "Manual")
    else:
        mainapp.set_parameter("Input;Lobulus Selection Method", "Auto")
    mainapp.run_lobuluses(seeds_mm=centers_mm)

    serverfile.process_started = False
    serverfile.save()
