"""
Tidy handling of images in Jupyter notebooks.

@author: Boris Gorelik
"""
import os
import shutil

import matplotlib.pylab as plt
from IPython.display import display, Image


class FigureDisplay:
    """

    Handle images in Jupyter notebook.

    Frequently, we want to re-use images generated in a Jupyter notebooks.
    To do that, on may either copy the image to the clipboard and save it elsewhere
    or, alternatively, make sure to call `fig.savefig` every time a figure is created.
    This class aims to make the later process simpler and with fewer boilerplate code.
    At the beginning of a notebook,  instantiate an object with a report name. Then,
    by simply calling the object, as if it was a function, a numbered figure file
    will be created in a dedicated folder. Additionally, the figure will be displayed in
    the notebook. To only save the figure, without displaying it, use the `figsave` function.

    """

    def __init__(self, report_name, show_title=True, parent_directory='figures', **suptitle_kwargs):
        """
        Create a callable image handler.
        Every image that will be handled by this object will be saved in the directory tree
        <parnt_directory>/<report_name> and will have the name pattern figure_XXX.png, where
        'XXX' is the running number with at least two leading zeros.

        Note: when the object is created, all the previous files in  <parnt_directory>/<report_name>
        will be silently deleted!

        :param report_name: string. The name of the report. Used to create a directory tree.
        :param show_title: boolean. Should the title be included in the figure? When saving or displaying
            the figure, one may supply an optional title argument. If `show_title` is True, this title
            will be included in the figure using `fig.suptitle` call. Setting `show_title=False` is useful
            when one needs to generate figures for a presentation program (such as PowerPoint) and doesn't
            want the figure titles to interfere with the slide titles. This way, by changing only one
            parameter, we achieve a report-wide effect.
            Default: True
        :param parent_directory: string. The name of the parent directory. Default: 'figures'
        :param suptitle_kwargs: If adding a title to the figure, will use pass optional arguments
            to `fig.suptitle`
        """
        self.report_name = report_name
        self.show_title = show_title
        self.current_number = 1
        self.suptitle_kwargs = dict(ha="left", ma="left", x=0, va='bottom')
        self.suptitle_kwargs.update(suptitle_kwargs)

        parent_directory = os.path.abspath(parent_directory)
        self.dir_name = os.path.join(parent_directory, report_name)
        try:
            shutil.rmtree(self.dir_name)
        except OSError:
            pass
        os.makedirs(self.dir_name)

    def figsave(self, fig, title=None):
        """ Save the figure without displaying it

        @param fig: matplotoib figure object
        @param title: either a string or None. If not None, and `self.show_title` is True, add
            this title to the figure. Default: None
        """
        if self.show_title == True and title is not None:
            fig.suptitle(title, **self.suptitle_kwargs)
        current_figure_number = self.current_number
        fname = os.path.join(self.dir_name, "figure_%03d.png" % current_figure_number)
        fig.savefig(fname, bbox_inches='tight', facecolor=fig.get_facecolor())
        self.current_number += 1
        plt.close(fig)
        return fname

    def figdisp(self, fig, title=None):
        """ Display and safe a figure. See `figsave` documentation. """
        fname = self.figsave(fig, title)
        return display(Image(fname))

    def __call__(self, fig=None, title=None):
        """ Alias to `figdisp` """
        if fig is None:
            fig = plt.gcf()
        return self.figdisp(fig, title)
