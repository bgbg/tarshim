"""
Tidy handling of images in Jupyter notebooks.

@author: Boris Gorelik
"""
import os
import shutil
import warnings
from typing import Literal

import matplotlib.pylab as plt
from IPython.display import display, Image
import matplotlib_inline.backend_inline


class FigureDisplay:
    """

    Handle images in Jupyter notebook.

    Frequently, we want to re-use images generated in a Jupyter notebooks.
    To do that, one may either copy the image to the clipboard and save it elsewhere
    or, alternatively, make sure to call `fig.savefig` every time a figure is created.
    This class aims to make the later process simpler and with fewer boilerplate code.
    At the beginning of a notebook,  instantiate an object with a report name. Then,
    by simply calling the object, as if it was a function, a numbered figure file
    will be created in a dedicated folder. Additionally, the figure will be displayed in
    the notebook. To only save the figure, without displaying it, use the `figsave` function.

    """

    def __init__(
        self,
        *,
        show_title: bool = True,
        parent_directory: str = "figures",
        when_parent_exists: Literal["delete", "error", "keep"] = "delete",
        first_figure_number: int = 1,
        face_color: str = "auto",
        **suptitle_kwargs,
    ):
        """
        Create a callable image handler.
        Every image that will be handled by this object will be saved in the directory tree
        <parnt_directory>/<report_name> and will have the name pattern figure_XXX.png, where
        'XXX' is the running number with at least two leading zeros.

        Note: when the object is created, all the previous files in  <parnt_directory>/<report_name>
        will be silently deleted!

        :param show_title. Should the title be included in the figure? When saving or displaying
            the figure, one may supply an optional title argument. If `show_title` is True, this title
            will be included in the figure using `fig.suptitle` call. Setting `show_title=False` is useful
            when one needs to generate figures for a presentation program (such as PowerPoint) and doesn't
            want the figure titles to interfere with the slide titles. This way, by changing only one
            parameter, we achieve a report-wide effect.
            Default: True
        :param parent_directory. The name of the parent directory. Default: 'figures'
        :param when_parent_exists. What to do when the parent directory already exists.
        :param first_figure_number. The number of the first figure. Default: 1
        :param face_color. The face color of the figure. 'auto', 'none', 'transparent' or a color spec. Default: 'auto'.
        If face_color is 'auto', the color is set to be the same as the background color of the first `axis`.
        If `face_color` is 'none' or 'transparent', the
        background is transparent. Otherwise, the color is set to the value of `face_color`.

        :param suptitle_kwargs: If adding a title to the figure, will use pass optional arguments
            to `fig.suptitle`
        """
        self.show_title = show_title
        self.current_number = first_figure_number
        self.suptitle_kwargs = dict(ha="left", ma="left", x=0, va="bottom")
        self.suptitle_kwargs.update(suptitle_kwargs)
        if when_parent_exists not in ["delete", "error", "keep"]:
            raise ValueError(
                f"when_parent_exists must be one of 'delete', 'error', 'keep'. Got {when_parent_exists}"
            )
        self.when_parent_exists = when_parent_exists
        self.face_color = face_color

        parent_directory = os.path.abspath(parent_directory)
        self.dir_name = parent_directory
        if os.path.exists(self.dir_name):
            if self.when_parent_exists == "delete":
                for filename in os.listdir(self.dir_name):
                    filepath = os.path.join(self.dir_name, filename)
                    try:
                        shutil.rmtree(filepath)
                    except OSError:
                        os.remove(filepath)
            elif self.when_parent_exists == "error":
                raise FileExistsError(
                    f"Directory {self.dir_name} already exists. Please delete it or change the report name."
                )
            elif self.when_parent_exists == "keep":
                warnings.warn(f"Directory {self.dir_name} already exists. Using it.")
            else:
                raise ValueError(
                    f"when_parent_exists must be one of 'delete', 'error', 'keep'. Got {when_parent_exists}"
                )
        else:
            os.makedirs(self.dir_name)

    def figsave(self, fig: plt.Figure = None, title: str = None) -> str:
        """ Save the figure without displaying it

        :param fig: matplotoib figure object
        :param title: either a string or None. If not None, and `self.show_title` is True, add
            this title to the figure. Default: None
        :return: the name of the saved file
        """
        if fig is None:
            fig = plt.gcf()
        if self.show_title is True and title is not None:
            fig.suptitle(title, **self.suptitle_kwargs)
        current_figure_number = self.current_number
        fname = os.path.join(self.dir_name, "figure_%03d.png" % current_figure_number)
        if self.face_color == "auto":
            face_color = fig.axes[0].get_facecolor()
        elif self.face_color in ["none", "transparent"]:
            face_color = None
        else:
            face_color = self.face_color
        fig.savefig(fname, bbox_inches="tight", facecolor=face_color)
        self.current_number += 1
        plt.close(fig)
        return fname

    def figdisp(self, fig: plt.Figure = None, title: str = None):
        """ Display and safe a figure. See `figsave` documentation. """
        if fig is None:
            fig = plt.gcf()
        fname = self.figsave(fig, title)
        return display(Image(fname))

    def __call__(self, fig: plt.Figure = None, title: str = None):
        """ Alias to `figdisp` """
        return self.figdisp(fig, title)

    @property
    def last_image_name(self):
        """ The name of the last saved figure. """
        return os.path.join(
            self.dir_name, "figure_%03d.png" % (self.current_number - 1)
        )


def auto_handling(*args, **kwargs):
    handler = FigureDisplay(*args, **kwargs)

    def flush_figures(*args, **kwargs):
        print("llll")
        ret = handler(*args, **kwargs)
        print("aaaa")
        return ret

    return flush_figures
