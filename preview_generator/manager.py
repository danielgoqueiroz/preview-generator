# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import typing

from preview_generator.preview.builder.office__libreoffice import OfficePreviewBuilderLibreoffice  # nopep8
from preview_generator.preview.builder_factory import PreviewBuilderFactory
from preview_generator.utils import ImgDims


class PreviewManager(object):
    cache_path = ''

    def __init__(self, path: str, create_folder: bool=False) -> None:
        """
        :param path: path to the cache folder.
        This is where previews will be stored
        :param create_folder: if True, then create the cache folder
        if it does not exist
        """

        path = os.path.join(path, '')  # add trailing slash
        # nopep8 see https://stackoverflow.com/questions/2736144/python-add-trailing-slash-to-directory-string-os-independently

        self.cache_path = path
        self._factory = PreviewBuilderFactory.get_instance()  # nopep8 keep link to singleton instance as it will be often used

        if create_folder:
            try:
                os.makedirs(self.cache_path)
            except OSError as e:
                logging.error(
                    'cant create cache folder [{}]'.format(self.cache_path)
                )

    def get_original_size(
            self,
            file_path: str,
            page: int =-1
    ) -> typing.Tuple[int, int]:
        mimetype = PreviewBuilderFactory().get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        size = builder.get_original_size(file_path, page)
        return size

    def get_nb_page(self, file_path: str) -> int:
        cache_path = self.cache_path
        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)

        preview_name = self._get_file_hash(file_path)
        page_nb = builder.get_page_number(file_path, preview_name, cache_path)
        return page_nb

    def get_jpeg_preview(
            self,
            file_path: str,
            page: int = -1,
            height: int = 256,
            width: int = None,
            force: bool = False,
            use_original_filename: bool = False,
            with_original_size: bool = False,
    ) -> str:

        if with_original_size:
            width = None
            height = None

        if width is None:
            width = height

        size = ImgDims(width=width, height=height)

        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.jpeg'
        if isinstance(builder, OfficePreviewBuilderLibreoffice):
            file_path = self.get_pdf_preview(
                file_path=file_path,
                page=page,
                force=force,
                use_original_filename=use_original_filename
            )
            preview_name = self._get_file_hash(
                file_path=file_path,
                size=size,
                page=page,
                use_original_filename=False
            )
        else:
            preview_name = self._get_file_hash(
                file_path=file_path,
                size=size,
                page=page,
                use_original_filename=False
            )

        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)

        # try:
        if force or not self.exists_preview(
                self.cache_path + preview_name,
                extension
        ):
            builder.build_jpeg_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                page_id=page,
                extension=extension,
                size=size
            )

        if page == -1:
            return self.cache_path + preview_name + extension
        else:
            return '{cache}{file}{ext}'.format(
                cache=self.cache_path,
                file=preview_name,
                ext=extension,
            )
        # except AttributeError:
        #     raise Exception('Error while getting the file the file preview')

    def get_pdf_preview(
            self,
            file_path: str,
            page: int = -1,
            force: bool = False,
            use_original_filename: bool = False
    ) -> str:

        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.pdf'
        preview_name = self._get_file_hash(
            file_path=file_path,
            page=page,
            use_original_filename=use_original_filename
        )
        try:
            if not self.exists_preview(
                    path=self.cache_path + preview_name,
                    extension=extension) or force:
                builder.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension,
                    page_id=page
                )

            if page is None or page <= -1:
                return '{path}{file_name}{extension}'.format(
                    path=self.cache_path,
                    file_name=preview_name,
                    extension=extension
                )
            else:
                return '{path}{file_name}{extension}'.format(
                    path=self.cache_path,
                    file_name=preview_name,
                    extension=extension
                )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_text_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = False
    ) -> str:

        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.txt'
        preview_name = self._get_file_hash(
            file_path=file_path,
            use_original_filename=use_original_filename)
        try:
            if not self.exists_preview(
                    path=self.cache_path + preview_name,
                    extension=extension
            ) or force:
                builder.build_text_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return '{cache}{file}{ext}'.format(
                cache=self.cache_path,
                file=preview_name,
                ext=extension,
            )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_html_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = False
    ) -> str:
        mimetype = self._factory.get_document_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.html'
        preview_name = self._get_file_hash(
            file_path,
            use_original_filename=use_original_filename
        )
        try:
            if not self.exists_preview(
                self.cache_path + preview_name,
                extension=extension
            ) or force:
                builder.build_html_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return '{cache}{file}{ext}'.format(
                cache=self.cache_path,
                file=preview_name,
                ext=extension,
            )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_json_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = False
    ) -> str:
        mimetype = self._factory.get_document_mimetype(file_path)
        logging.info('Mimetype of the document is :' + mimetype)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.json'
        preview_name = self._get_file_hash(
            file_path=file_path,
            use_original_filename=use_original_filename
        )
        if True:
            if not self.exists_preview(
                path=self.cache_path + preview_name,
                extension=extension
            ) or force:
                builder.build_json_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return self.cache_path + preview_name + extension
        # except AttributeError:
        #     raise Exception('Error while getting the file preview')

    def _get_file_hash(
            self,
            file_path: str,
            size: ImgDims=None,
            page: int = None,
            use_original_filename: bool = False
    ) -> str:
        if '.' in file_path:
            tab_str = file_path.split('.')
            file_path = ''
            for index in range(0, len(tab_str) - 1):
                file_path = file_path + tab_str[index]

        file_name = []
        if use_original_filename:
            file_name.append(os.path.basename(file_path))

        if size:
            file_name.append('{fh}x{fw}'.format(
                fh=size.width,
                fw=size.height
            ))
        file_name.append(hashlib.md5(file_path.encode('utf-8')).hexdigest())

        if page is not None and page > -1:
            file_name.append('page{page}'.format(page=page))

        return '-'.join(file_name)

    def exists_preview(
            self,
            path: str,
            extension: str = ''
    ) -> bool:
        """
        return true if the cache file exists
        """
        full_path = '{path}{extension}'.format(
            path=path,
            extension=extension
        )

        if os.path.exists(full_path):
            return True
        else:
            return False