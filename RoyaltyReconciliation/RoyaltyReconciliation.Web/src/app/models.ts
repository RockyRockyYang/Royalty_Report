export interface FileReport {
    content: string;
    sheetList: string[];
    fullPath: string;
    actionResponse: {};
    success: boolean;
}

export interface Argv {
    fullPath: string;
    currSheet: string;
}